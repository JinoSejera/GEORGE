from pydantic import BaseModel
from typing import Optional, Iterable, List


class WebSearchResultRef(BaseModel):
    no:int
    title:str
    link:str
    snippet:str


class OrganicResult(BaseModel):
    answer:str
    references: Optional[List[WebSearchResultRef]]
    
class WebSearchResult(BaseModel):
    organic_result: OrganicResult
