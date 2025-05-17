from pydantic import BaseModel
from typing import Dict, List, Any

class ResponseBody(BaseModel):
    name:str
    message:str
    kb_results: List[Dict[str, Any] | None]
    web_search_results: Any | Dict[str, Dict[str, Any]]
    chat_history:str