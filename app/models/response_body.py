from pydantic import BaseModel
from typing import Optional, List

from .knowledge_base_model import PodCastKnowledgeBaseModel
from .web_search_result_model import WebSearchResult

class ResponseBody(BaseModel):
    name:str
    message:str
    kb_results: Optional[List[PodCastKnowledgeBaseModel]] = []
    web_search_results: WebSearchResult
    chat_history:str