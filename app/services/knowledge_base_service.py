import logging
import asyncio

from ..models.knowledge_base_model import PodCastKnowledgeBaseModel
from ..utils.transcripts import TRANSCRIPTS
from ..contract.memory_repository_base import MemoryRepositoryBase

logger = logging.getLogger(__name__)
max_concurrency = 5

class KnowledgeBaseService:
    """
    Service for managing the knowledge base, including ingestion and search.
    """
    __kb: "MemoryRepositoryBase"
    def __init__(self, kb: MemoryRepositoryBase):
        """
        Initialize the KnowledgeBaseService.

        Args:
            kb (MemoryRepositoryBase): The memory repository instance.
        """
        self.__kb = kb
        self.__semaphore = asyncio.Semaphore(max_concurrency)
        
    async def __safe_save(self, metadata: PodCastKnowledgeBaseModel):
        """
        Safely save metadata to the knowledge base with concurrency control.

        Args:
            metadata (PodCastKnowledgeBaseModel): The metadata to save.
        """
        async with self.__semaphore:
            logger.info(f"Ingesting: {metadata.id}")
            await self.__kb.save_memory_async(metadata)
            
    async def ingest_transcripts_async(self):
        """
        Ingest all transcripts into the knowledge base asynchronously.
        """
        try:
            for transcript in TRANSCRIPTS:
                tasks = []
                for i, time_stamp in enumerate(transcript["transcripts"], start=1):
                    metadata = PodCastKnowledgeBaseModel(
                        id=f"{transcript['title']}-{i}",
                        podcast_title=transcript["title"],
                        content = time_stamp["content"],
                        time_stamp=time_stamp["time_stamp"]
                    )
                    logger.info(f"Ingesting: {metadata.id}")
                    tasks.append(self.__safe_save(metadata))
                await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error encountered During ingestion: {e}")
            raise e
        
    async def search_kb_async(self, query:str):
        """
        Search the knowledge base asynchronously.

        Args:
            query (str): The search query.

        Returns:
            Any: The search result.
        """
        return await self.__kb.search_memory_async(query)

