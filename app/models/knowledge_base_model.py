from typing import Optional

from pydantic import BaseModel
    
class PodCastKnowledgeBaseModel(BaseModel):
    id: str
    score: float
    podcast_title: str
    content: str
    time_stamp: Optional[str] = None