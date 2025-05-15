from abc import abstractmethod, ABC

from typing import Optional, Dict, Any

from ..models.knowledge_base_model import PodCastKnowledgeBaseModel

INDEX_NAME = "georgekb"

class MemoryRepositoryBase(ABC):
    @abstractmethod
    async def save_memory_async(self, metadata: PodCastKnowledgeBaseModel) -> None:
        """
        Save a memory (knowledge base entry) asynchronously.

        Args:
            metadata (PodCastKnowledgeBaseModel): The metadata to save.
        """
        pass
    
    @abstractmethod
    async def search_memory_async(self, query:str,collection:str=INDEX_NAME,min_relevance_score:float=0.6)->Optional[Dict[str, Any]]:
        """
        Search the memory (knowledge base) asynchronously.

        Args:
            query (str): The search query.
            collection (str, optional): The collection/index name. Defaults to INDEX_NAME.
            min_relevance_score (float, optional): Minimum relevance score for results. Defaults to 0.6.

        Returns:
            Optional[Dict[str, Any]]: The search result or None.
        """
        pass
    
    @abstractmethod
    async def initialize_knowledge_base_async(self) -> None:
        """
        Initialize the knowledge base asynchronously.
        """
        pass