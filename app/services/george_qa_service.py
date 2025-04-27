import logging
import json
from typing import List, Iterable, Any
import asyncio
import ast

from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments

from ..services.knowledge_base_service import KnowledgeBaseService 
from ..models.knowledge_base_model import PodCastKnowledgeBaseModel
from ..models.web_search_result_model import WebSearchResult
from ..contract.kernel_repository_base import KernelRepositoryBase
from ..connectors.search_engine.bing_serapi_connector import SearchConnectorBase

logger = logging.getLogger(__name__)

class GeorgeQAService:
    __kernel: "KernelRepositoryBase"
    __memory_service: "KnowledgeBaseService"
    __search_connector: "SearchConnectorBase"
    
    def __init__(self, kernel: KernelRepositoryBase, 
                 memory_service: KnowledgeBaseService,
                 search_connector: SearchConnectorBase) -> None:
        self.__kernel = kernel
        self.__memory_service = memory_service
        self.__search_connector = search_connector
        
    async def ask_async(self, query:str, chat_history:ChatHistory):
        try:
            # Break down the query into smaller queries for better results
            # This is done by the QueryStructuringPlugin in the kernel.
            re_queries_task = self.breakdown_query_async(query,chat_history)
            re_generate_query_task = self.regenerate_query_async(query, chat_history)
            
            re_queries, re_generate_query = await asyncio.gather(re_queries_task, re_generate_query_task)
            logger.warning(f"Re-composed queries: {re_queries}\nRe-generated query: {re_generate_query}")
            
            # Retrieve stored knowledge base results for each re-composed query
            # This is done by the KnowledgeBaseService in the kernel.
            kb_task= asyncio.gather(*(self.__memory_service.search_kb(query) for query in re_queries['recomposed_queries']))
            
            # Perform web search using the Bing web search API
            # This is done by the WebSearchEnginePlugin in the kernel.
            web_search_task = self.__search_connector.search(re_generate_query, num_results=3)
            
            # Run KB search and web search in parallel
            kb_results, web_search_results = await asyncio.gather(kb_task, web_search_task)
            
            # Flatten kb_results if it's a list of lists
            if any(isinstance(item, list) for item in kb_results):
                kb_results = [elem for sublist in kb_results for elem in sublist]

            # Remove duplicates using (podcast_title, time_stamp) as the unique key
            if(kb_results):
                seen = set()
                unique_kb_results = []
                for item in kb_results:
                    key = (item.get("podcast_title"), item.get("timpe_stamp"))
                    if key not in seen:
                        unique_kb_results.append(item)
                        seen.add(key)
                kb_results = unique_kb_results
                            
                logger.warning(f"KB Results: {kb_results}")
            
            ## Convert the results to the appropriate models
            if not isinstance(web_search_results, dict):
                web_search_results = json.loads(web_search_results)
            
            logger.warning(f"Web Search Results: {web_search_results}")
                    
            george_response = await self.__kernel.ask(query, chat_history, kb_results, web_search_results)
            
            web_search_results = WebSearchResult(**web_search_results)
            kb_results = [
                PodCastKnowledgeBaseModel(**kb_result) for kb_result in kb_results
            ] if kb_results else None
            
            return george_response, kb_results, web_search_results
        
        except Exception as e:
            logger.error(f"Encountered Error: {e}")
            raise e
    
    async def breakdown_query_async(self, query:str, chat_history:ChatHistory)-> dict[str, str]:
        try:
            return json.loads((await self.__kernel.breakdown_query(query,chat_history)))
        except Exception as e:
            logger.error(f"Encountered Error: {e}")
            raise e
        
    async def regenerate_query_async(self, query:str, chat_history:ChatHistory)-> str:
        try:
            return await self.__kernel.regenerate_query(query,chat_history)
        except Exception as e:
            logger.error(f"Encountered Error: {e}")
            raise e