# import asyncio
# import logging

# from ..models.knowledge_base_model import PodCastKnowledgeBase
# from ..repository.kernel_repository import KernelRepository

# from semantic_kernel import Kernel
# from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
# from semantic_kernel.connectors.memory.azure_ai_search import AzureAISearchCollection

# INDEX_NAME = "PODCAST_TRANSCRIPTS"

# from semantic_kernel.data import (
#     VectorSearchOptions,
# )
# from semantic_kernel.data.vector_search import add_vector_to_records

# first_run = False

# logger = logging.getLogger(__name__)


# async def add_vectors(collection: AzureAISearchCollection, kernel: Kernel):
#     """
#     This is a simple function that uses the add_vector_to_records function to add vectors.

#     It first uses the search_client within the collection to get a list of ids.
#     and then uses the upsert to add the vectors to the records.
#     """
    
#     ids: list[str] = [res.get("podcast_id") async for res in await collection.search_client.search(select="podcast_id")]
#     logging.info("sample id", ids[0])
    
#     podcasts = await collection.get_batch(ids)
#     if podcasts is not None and isinstance(podcasts, list):
#         for podcast in podcasts:
#             if not podcast.content_vector:
#                 podcast = await add_vector_to_records(kernel, podcast, PodCastKnowledgeBase)
 
# async def initialize():
#     kernel_repo = KernelRepository()
#     kernel = kernel_repo.get_kernel()
#     embedding = kernel_repo.get_embedding_service()
    
#     collection = AzureAISearchCollection[str, PodCastKnowledgeBase](collection_name=INDEX_NAME, data_model_type=PodCastKnowledgeBase,se)

import logging
import json

from semantic_kernel.memory import SemanticTextMemory

from ..services.memory_store_service import get_memory_store
from ..repository.kernel_repository import KernelRepository
from ..models.knowledge_base_model import PodCastKnowledgeBaseModel
from ..utils.singleton_decorator import singleton

logger = logging.getLogger(__name__)
INDEX_NAME = "georgekb"

@singleton
class KnowledgeBaseRepository:
    def __init__(self, kernel:KernelRepository = KernelRepository()):
        self.__knowledge_base = get_memory_store()
        self.__memory = SemanticTextMemory(storage=self.__knowledge_base,
                                           embeddings_generator=kernel.get_embedding_service())
        
    async def save_memory(self, metadata: PodCastKnowledgeBaseModel):
        additional_metadata = {
            "time_stamp":metadata.time_stamp
        }
        await self.__memory.save_information(collection=INDEX_NAME,
                                             id=metadata.id,
                                             description=metadata.podcast_title,
                                             text=metadata.content,
                                             additional_metadata=json.dumps(additional_metadata))
    
    async def search_memory(self, query:str)->dict:
        result = await self.__memory.search(collection=INDEX_NAME,query=query,min_relevance_score=0.6)
        if(len(result) !=0 ):
            metadata:dict = json.loads(result[0].additional_metadata)
            return {
                "title": result[0].description,
                "content": result[0].text,
                "time_stamp": metadata.get("time_stamp", "")
            }
        else:
            return {
                "title": "",
                "content": "",
                "time_stamp": ""
            }
    async def initialize_knowledge_base(self):
        async with self.__knowledge_base as kb:
            if(not await kb.does_collection_exist(INDEX_NAME)):
                logger.info(f"Index {INDEX_NAME} does not exist. Initializing creation.")
                await kb.create_collection(INDEX_NAME)