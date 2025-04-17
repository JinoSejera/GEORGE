import logging
import asyncio
from ..utils.transcripts import TRANSCRIPTS

from ..repository.knowledge_base_repository import KnowledgeBaseRepository
from ..models.knowledge_base_model import PodCastKnowledgeBaseModel

logger = logging.getLogger(__name__)
max_concurrency = 5

class KnowledgeBaseService:
    def __init__(self, kb: KnowledgeBaseRepository):
        self.__kb = kb
        self.__semaphore = asyncio.Semaphore(max_concurrency)
        
    async def _safe_save(self, metadata: PodCastKnowledgeBaseModel):
        async with self.__semaphore:
            logger.info(f"Ingesting: {metadata.id}")
            await self.__kb.save_memory(metadata)
            
    async def ingest_transcripts(self):
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
                    tasks.append(self._safe_save(metadata))
                await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error encountered During ingestion: {e}")
            raise e
        
    async def search_kb(self, query:str)->dict:
        return await self.__kb.search_memory(query)

        