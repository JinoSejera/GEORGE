import logging
import json
from typing import Optional, Any, Dict

from semantic_kernel.memory import SemanticTextMemory

from ..services.memory_store_service import get_memory_store
from ..services.oai_services import get_embedding_service
from ..models.knowledge_base_model import PodCastKnowledgeBaseModel
from ..utils.singleton_decorator import singleton
from ..contract.memory_repository_base import MemoryRepositoryBase
logger = logging.getLogger(__name__)
INDEX_NAME = "georgekb"

@singleton
class KnowledgeBaseRepository(MemoryRepositoryBase):
    def __init__(self):
        self.__knowledge_base = get_memory_store()
        self.__memory = SemanticTextMemory(storage=self.__knowledge_base,
                                           embeddings_generator=get_embedding_service())
        
    async def save_memory(self, metadata: PodCastKnowledgeBaseModel):
        additional_metadata = {
            "time_stamp":metadata.time_stamp
        }
        await self.__memory.save_information(collection=INDEX_NAME,
                                             id=metadata.id,
                                             description=metadata.podcast_title,
                                             text=metadata.content,
                                             additional_metadata=json.dumps(additional_metadata))
    
    async def search_memory(self, query:str,collection:str=INDEX_NAME,min_relevance_score:float=0.6)->Optional[Dict[str, Any]]:
        result = await self.__memory.search(
            collection=collection,
            query=query,
            min_relevance_score=min_relevance_score)
        
        if result:
            metadata = json.loads(result[0].additional_metadata or "{}")
            # return PodCastKnowledgeBaseModel(
            #     id=result[0].id,
            #     podcast_title=result[0].description,  # Assuming this maps correctly
            #     score=result[0].relevance,
            #     content=result[0].text,
            #     time_stamp=metadata.get("time_stamp")
            # )
            return {
                "id": result[0].id,
                "podcast_title": result[0].description,  # Assuming this maps correctly
                "score": result[0].relevance,
                "content": result[0].text,
                "time_stamp": metadata.get("time_stamp")
            }
        return None
        
    async def initialize_knowledge_base(self):
        async with self.__knowledge_base as kb:
            if(not await kb.does_collection_exist(INDEX_NAME)):
                logger.info(f"Index {INDEX_NAME} does not exist. Initializing creation.")
                await kb.create_collection(INDEX_NAME)