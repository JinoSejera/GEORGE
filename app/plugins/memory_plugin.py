import logging 
from typing import Annotated, List, Set, Tuple
import json
import asyncio

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from ..services.knowledge_base_service import KnowledgeBaseService
from ..models.knowledge_base_model import PodCastKnowledgeBaseModel

logger = logging.getLogger(__name__)

class GeorgeMemoryPlugin:
    """ A plugin to fetch memory with GEORGE Knowledge Base"""
    
    __memory_service: KnowledgeBaseService
    
    def __init__(self, memory_service: KnowledgeBaseService):
        self.__memory_service = memory_service
        
    @kernel_function(description="Recall a memory from knowledge base/long term memory",
                     name="recall")
    async def recall(
      self,
      query: Annotated[str, "the query used to retrieve memory."],
      kernel: Annotated["Kernel", "The kernel instance."]
    ):
        """ Recall a memory from knowledge base/long term memory 
        """
        try:
            re_query_func = kernel.get_function("QueryStructuringPlugin", "RecomposeQuery")
            
            queries_dict:dict = json.loads(str(await kernel.invoke(re_query_func,KernelArguments(query=query))))
            queries = queries_dict['recomposed_queries']
            
            kb_results = await asyncio.gather(*(self.__memory_service.search_kb(query) for query in queries))
                    
            # Remove duplicates by using frozenset or hashable structure for uniqueness
            kb_results = self.__filter_unique_by_title_and_timestamp(kb_results)
            
            # logger.warning(
            #     [kb_result.model_dump() for kb_result in kb_results]
            # )
            
            return json.dumps([kb_result.model_dump() for kb_result in kb_results])
        

        except Exception as e:
            logger.error(f"Error retrieving KB results: {e}")
            return []  # Or handle accordingly
        
    def __filter_unique_by_title_and_timestamp(
        self,
        results: List[PodCastKnowledgeBaseModel]
    ) -> List[PodCastKnowledgeBaseModel]:
        seen: Set[Tuple[str, str]] = set()
        unique_results: List[PodCastKnowledgeBaseModel] = []

        for item in results:
            key = (item.podcast_title, item.time_stamp or "")
            if key not in seen:
                seen.add(key)
                unique_results.append(item)

        return unique_results