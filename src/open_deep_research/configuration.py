import os
from enum import Enum
from dataclasses import dataclass, fields 
from typing import Any, Optional, Dict 

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig


DEFAULT_REPORT_STRUCTURE = """Use this structure to create a report on the user-provided topic:

1. Introduction (no research needed)
   - Brief overview of the topic area

2. Main Body Sections:
   - Each section should focus on a sub-topic of the user-provided topic
   
3. Conclusion
   - Aim for 1 structural element (either a list of table) that distills the main body sections 
   - Provide a concise summary of the report"""


class search_API(Enum):
    Tavily = "tavily"

@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the chatbot."""
    report_structure: str = DEFAULT_REPORT_STRUCTURE 
    max_search_depth: int = 2
    number_of_queries: int= 2
    planner_provider: str = "nvidia"  
    planner_model: str = "meta/llama-3.1-70b-instruct" 
    writer_provider: str = "nvidia"
    writer_model: str = "meta/llama-3.1-70b-instruct" 
    search_api: SearchAPI = SearchAPI.TAVILY 
    search_api_config: Optional[Dict[str, Any]] = None 


    @classmethod
    def from_runnable_config(cls, config: Optional[RunnableConfig] = None) -> "Configuration":
        configurable = (
            config['configurable'] if config and "configurable" in config else {} 
        )
        values: dict[str: Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.int 
        }
        return cls(**{k: v for k, v in values.items() if v})
