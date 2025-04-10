import os 
import asyncio
import requests 
import random 
import concurrent 
import aiohttp
import time 
import logging

from typing import List, Optional, Dict, Any, Union
from urllib.parse import unquote

from tavily import AsyncTavilyClient
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup

from langchain_community.retrivers import ArvixRetriver
from langsmith import traceable

from open_deep_research.state import Section


def get_config_value(value):
    """
    Helper function to handle both string and enum cases of configuration values
    """
    if isinstance(value, str):
        return value
    return getattr(value, 'value', value)




def get_search_params(search_api: str, search_api_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Filters and returns valid parameters for a specified search API based on a given configuration.

    Args:
        search_api (str): The name of the search API (e.g., "tavily", "arvix").
        search_api_config (Optional[Dict[str, Any]]): A dictionary of parameters provided for the search API.

    Returns:
        Dict[str, Any]: A dictionary containing only the parameters that are accepted by the specified search API.
                        Returns an empty dictionary if no valid config is provided or if no parameters match.
    """
    SEARCH_API_PARAMS = {
        "tavily": [],
        "arvix": ["load_max_docs", "get_full_documents", "load_all_available_meta"]
    }

    accepted_params = SEARCH_API_PARAMS.get(search_api, [])

    if not search_api_config:
        return {}

    return {k: v for k, v in search_api_config.items() if k in accepted_params}




def duplicate_and_format_source(
    search_response: List[Dict[str, Any]],
    max_tokens_per_source: int,
    include_raw_content: bool = True
) -> str:
    """
    Takes a list of search responses and formats them into a readable string.
    Limits the raw_content to approximately max_tokens_per_source tokens.

    Args:
        search_response (List[Dict[str, Any]]): A list of search API responses, each containing a
            - query: str
            - results: List of dicts with fields:
                - title: str
                - url: str
                - content: str
                - score: float
                - raw_content: str|None 'results' list.
        max_tokens_per_source (int): The max number of tokens allowed from raw content (used to limit length).
        include_raw_content (bool): Whether to include the full raw content from each source (truncated if too long).

    Returns:
        str: A formatted string containing the cleaned and formatted content from all unique sources.
    """

    source_list = []
    for response in search_response:
        source_list.extend(response['results'])

    # Deduplicate by URL
    unique_sources = {source['url']: source for source in source_list}

    # Format output
    formatted_text = "Content from sources:\n"
    for i, source in enumerate(unique_sources.values(), 1):
        formatted_text += f"{'=' * 80}\n"
        formatted_text += f"Source: {source.get('title', 'Untitled')}\n"
        formatted_text += f"{'-' * 80}\n"
        formatted_text += f"URL: {source.get('url', 'No URL')}\n===\n"
        formatted_text += f"Most relevant content from source: {source.get('content', '')}\n===\n"

        if include_raw_content:
            char_limit = max_tokens_per_source * 4  # Rough estimate: 4 characters per token
            raw_content = source.get('raw_content') or ''
            if not raw_content:
                print(f"Warning: No raw_content found for source {source.get('url', 'Unknown URL')}")
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "... [truncated]"
            formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"

        formatted_text += f"{'=' * 80}\n\n"

    return formatted_text.strip()


def format_sections(sections: list[Section]) -> str:
    """ Format a list of sections into a string """
    formatted_str = ""
    for idx, section in enumerate(sections, 1):
        formatted_str += f"""
{'='*60}
Section {idx}: {section.name}
{'='*60}
Description:
{section.description}
Requires Research: 
{section.research}

Content:
{section.content if section.content else '[Not yet written]'}

"""
    return formatted_str



def format_sections(sections: List['Section']) -> str:
    """
    Formats a list of Section objects into a readable, color-coded multi-section string.

    Args:
        sections (List[Section]): A list of Section objects, each with name, description, research, and content fields.

    Returns:
        str: A formatted and color-coded string with clearly separated sections.
    """

    # ANSI color codes
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'  # Reset to default

    formatted_str = ""
    for idx, section in enumerate(sections, 1):
        formatted_str += f"""
{YELLOW}{'='*60}
Section {idx}: {section.name}
{'='*60}{ENDC}
{BLUE}Description:{ENDC}
{section.description}

{GREEN}Requires Research:{ENDC}
{section.research}

{HEADER}Content:{ENDC}
{section.content if section.content else RED + '[Not yet written]' + ENDC}
"""
    return formatted_str.strip() 



@tracable
async def tavily_search_async(search_queries: List[str]) -> List[dict]:
     """
    Performs concurrent web searches using the Tavily API.

    Args:
        search_queries (List[SearchQuery]): List of search queries to process

    Returns:
            List[dict]: List of search responses from Tavily API, one per query. Each response has format:
                {
                    'query': str, # The original search query
                    'follow_up_questions': None,      
                    'answer': None,
                    'images': list,
                    'results': [                     # List of search results
                        {
                            'title': str,            # Title of the webpage
                            'url': str,              # URL of the result
                            'content': str,          # Summary/snippet of content
                            'score': float,          # Relevance score
                            'raw_content': str|None  # Full page content if available
                        },
                        ...
                    ]
                }
    """
    tavily_async_client = AsyncTavilyClient()
    search_tasks = [
        tavily_async_client.search(
            query,
            max_results=5,
            include_raw_content=True,
            topic="general"
        ) for query in search_queries
    ]

    search_docs = await asyncio.gather(*search_tasks)
    return search_docs


async def arvix_search_async(search_queries,
                             load_max_docs=5, 
                             get_full_documents=True,
                             load_all_available_meta=True):
    
     """
    Performs concurrent searches on arXiv using the ArxivRetriever.

    Args:
        search_queries (List[str]): List of search queries or article IDs
        load_max_docs (int, optional): Maximum number of documents to return per query. Default is 5.
        get_full_documents (bool, optional): Whether to fetch full text of documents. Default is True.
        load_all_available_meta (bool, optional): Whether to load all available metadata. Default is True.

    Returns:
        List[dict]: List of search responses from arXiv, one per query. Each response has format:
            {
                'query': str,                    # The original search query
                'follow_up_questions': None,      
                'answer': None,
                'images': [],
                'results': [                     # List of search results
                    {
                        'title': str,            # Title of the paper
                        'url': str,              # URL (Entry ID) of the paper
                        'content': str,          # Formatted summary with metadata
                        'score': float,          # Relevance score (approximated)
                        'raw_content': str|None  # Full paper content if available
                    },
                    ...
                ]
            }
    """

    async def process_single_query(query):
        try:
            retriever = ArxivRetriever(
                load_max_docs=load_max_docs,
                get_full_documents=get_full_documents,
                load_all_available_meta=load_all_available_meta
            )

            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(None, lambda: retriever.invoke(query))

            results = []
            base_score = 1.0
            score_decrement = 1.0 / (len(docs) + 1) if docs else 0

            for i, doc in enumerate(docs):
                metadata = doc.metadata
                url = metadata.get('entry_id', '')

                content_parts = []
                if 'Summary' in metadata:
                    content_parts.append(f"Summary: {metadata['Summary']}")
                if 'Authors' in metadata:
                    content_parts.append(f"Authors: {metadata['Authors']}")
                published = metadata.get('Published')
                published_str = published.isoformat() if hasattr(published, 'isoformat') else str(published) if published else ''
                if published_str:
                    content_parts.append(f"Published: {published_str}")
                if 'primary_category' in metadata:
                    content_parts.append(f"Primary Category: {metadata['primary_category']}")
                if 'categories' in metadata and metadata['categories']:
                    content_parts.append(f"Categories: {', '.join(metadata['categories'])}")
                if 'comment' in metadata and metadata['comment']:
                    content_parts.append(f"Comment: {metadata['comment']}")
                if 'journal_ref' in metadata and metadata['journal_ref']:
                    content_parts.append(f"Journal Reference: {metadata['journal_ref']}")
                if 'doi' in metadata and metadata['doi']:
                    content_parts.append(f"DOI: {metadata['doi']}")
                
                pdf_link = ""
                if 'links' in metadata and metadata['links']:
                    for link in metadata['links']:
                        if 'pdf' in link:
                            pdf_link = link
                            content_parts.append(f"PDF: {pdf_link}")
                            break

                content = "\n".join(content_parts)
                
                result = {
                    'title': metadata.get('Title', ''),
                    'url': url,
                    'content': content,
                    'score': base_score - (i * score_decrement),
                    'raw_content': doc.page_content if get_full_documents else None
                }
                results.append(result)

            return {
                'query': query,
                'follow_up_questions': None,
                'answer': None,
                'images': [],
                'results': results
            }
        except Exception as e:
            print(f"Error processing arXiv query '{query}': {str(e)}")
            return {
                'query': query,
                'follow_up_questions': None,
                'answer': None,
                'images': [],
                'results': [],
                'error': str(e)
            }

    # Process queries concurrently with a rate-limiting mechanism
    search_docs = []
    async def process_queries():
        for i, query in enumerate(search_queries):
            if i > 0:
                await asyncio.sleep(3.0)  # Respect arXiv's rate limit
            result = await process_single_query(query)
            search_docs.append(result)

    await process_queries()
    return search_docs


from ddgs import DDGS
import asyncio

@traceable
async def duckduckgo_search(search_queries):
    """Perform searches using DuckDuckGo
    
    Args:
        search_queries (List[str]): List of search queries to process
        
    Returns:
        List[dict]: List of search results
    """
    async def process_single_query(query):
        loop = asyncio.get_event_loop()
        
        def perform_search():
            results = []
            try:
                with DDGS() as ddgs:
                    ddg_results = list(ddgs.text(query, max_results=5))
                    
                    for i, result in enumerate(ddg_results):
                        results.append({
                            'title': result.get('title', ''),
                            'url': result.get('link', ''),
                            'content': result.get('body', ''),
                            'score': 1.0 - (i * 0.1),  # Simple scoring mechanism
                            'raw_content': result.get('body', '')
                        })
            except Exception as e:
                print(f"Error performing DuckDuckGo search for query '{query}': {str(e)}")
                return {
                    'query': query,
                    'follow_up_questions': None,
                    'answer': None,
                    'images': [],
                    'results': [],
                    'error': str(e)
                }
                
            return {
                'query': query,
                'follow_up_questions': None,
                'answer': None,
                'images': [],
                'results': results
            }

        return await loop.run_in_executor(None, perform_search)

    # Execute all queries concurrently
    tasks = [process_single_query(query) for query in search_queries]
    search_docs = await asyncio.gather(*tasks)
    
    return search_docs

async def select_and_execute_search(search_api: str, query_list: list[str], params_to_pass: dict) -> str:
    """Select and execute the appropriate search API.
    
    Args:
        search_api: Name of the search API to use
        query_list: List of search queries to execute
        params_to_pass: Parameters to pass to the search API
        
    Returns:
        Formatted string containing search results
        
    Raises:
        ValueError: If an unsupported search API is specified
    """
    try:
        # Validate input parameters
        if not isinstance(query_list, list) or not all(isinstance(query, str) for query in query_list):
            raise ValueError("query_list must be a list of strings")
        if not isinstance(params_to_pass, dict):
            raise ValueError("params_to_pass must be a dictionary")
        
        # Execute the appropriate search based on search_api
        if search_api == "tavily":
            search_results = await tavily_search_async(query_list, **params_to_pass)
            return deduplicate_and_format_sources(search_results, max_tokens_per_source=4000, include_raw_content=False)
        elif search_api == "arxiv":
            search_results = await arxiv_search_async(query_list, **params_to_pass)
            return deduplicate_and_format_sources(search_results, max_tokens_per_source=4000)
        elif search_api == "duckduckgo":
            search_results = await duckduckgo_search(query_list)
            return deduplicate_and_format_sources(search_results, max_tokens_per_source=4000)
        else:
            raise ValueError(f"Unsupported search API: {search_api}")

    except ValueError as ve:
        print(f"ValueError occurred: {ve}")
        raise  # Re-raise the ValueError to propagate it
    except Exception as e:
        print(f"An error occurred: {e}")
        raise  # Re-raise any other exception to propagate it

