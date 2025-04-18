from typing import Annotated, List, TypedDict, Literal
from pydantic import BaseModel, Field
import operator


class Section(BaseModel):
    name: str = Field(
        description = "Name for this section of the report"
    )
    description : str = Field(
        description = "Brief overview of the main topics and concepts to be covered in this section. ",
    )
    research: bool = Field(
        description = "Whether to perform web research for this section of the report"
    )
    content: str = Field(
        description = "The content of the section"
    )


class Sections(BaseModel):
    sections: List[Section] = Field(
        description="Sections of the report.",
    )

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Query for web search.")


class Queries(BaseModel):
    queries: List[SearchQuery] = Field(
        description="List of search queries.",
    )


class Feedback(BaseModel):
    grade: Literal["pass","fail"] = Field(
        description="Evaluation result indicating whether the response meets requirements ('pass') or needs revision ('fail')."
    )
    follow_up_queries: List[SearchQuery] = Field(
        description="List of follow-up search queries.",
    )


class ReportState(TypedDict):
    topic: str    
    feedback_on_report_plan: str 
    sections: list[Section] 
    completed_sections: Annotated[list, operator.add] # Send() API key
    report_sections_from_research: str 
    final_report: str # Final report

class SectionState(TypedDict):
    topic: str #
    section: Section  
    search_iterations: int 
    search_queries: list[SearchQuery] 
    source_str: str 
    report_sections_from_research: str 
    completed_sections: list[Section] 

class SectionOutputState(TypedDict):
    completed_sections: list[Section] 
