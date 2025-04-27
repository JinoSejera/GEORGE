from abc import abstractmethod, ABC

import logging
import json
from typing import Optional, Dict, Any

from semantic_kernel.memory import SemanticTextMemory

from ..services.memory_store_service import get_memory_store
from ..services.oai_services import get_embedding_service
from ..models.knowledge_base_model import PodCastKnowledgeBaseModel
from ..utils.singleton_decorator import singleton

INDEX_NAME = "georgekb"

class MemoryRepositoryBase(ABC):
    @abstractmethod
    async def save_memory(self, metadata: PodCastKnowledgeBaseModel) -> None:
        pass
    
    @abstractmethod
    async def search_memory(self, query:str,collection:str=INDEX_NAME,min_relevance_score:float=0.6)->Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def initialize_knowledge_base(self) -> None:
        pass