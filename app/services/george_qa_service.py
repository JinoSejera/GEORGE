import logging
import json
from typing import List, Iterable, Any, Dict, Optional, Tuple
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
        
    async def ask_async(self,query:str, chat_history:ChatHistory):
        try:
            
            kb_results, web_search_results = await self._get_information_async(query, chat_history)
            
            george_response = await self.__kernel.ask(query, chat_history, kb_results, web_search_results)
            
            web_search_results = WebSearchResult(**web_search_results)
            kb_results = [
                PodCastKnowledgeBaseModel(**kb_result) for kb_result in kb_results
            ] if kb_results else None
            
            return george_response, kb_results, web_search_results
        
        except Exception as e:
            logger.error(f"Encountered Error: {e}")
            raise e
        
    async def ask_streaming_async(self,query:str, chat_history:ChatHistory):
        try:
            # Streaming response content
            message_accumulator = ""
            
            result_from_history = await self.__kernel.check_history(query, chat_history)
            
            if result_from_history.lower() != "no answer":
                logger.warning(f"Agent Response - result from history: {result_from_history}")
                for chunk in result_from_history.split(" "):
                    message_accumulator += f"{chunk} "
                    yield f"{chunk} "
                    # logger.warning(f"Chunk: {chunk}")
                    await asyncio.sleep(0.1)

                chat_history = self._add_to_chat_history(chat_history, query, result_from_history)
                final_response = self._final_response(message = message_accumulator.strip(), chat_history=chat_history)
                
                await asyncio.sleep(0.1)  # ensure async yield
                yield f"\n<|END_OF_RESPONSE|>\n{json.dumps(final_response)}"
                logger.info(f"Final Response - result from history: \n<|END_OF_RESPONSE|>\n{json.dumps(final_response)}")
                return  # 🚨 Important: do not continue to OpenAI call!
            
            kb_results, web_search_results = await self._get_information_async(query, chat_history)
            
            if not kb_results or len(kb_results) == 0:
                fallback_message = "I am sorry, but I do not have enough information to answer that."
                logger.info(f"Agent Response - info not sufficient: {fallback_message}")
                for chunk in fallback_message.split(" "):
                    message_accumulator += f"{chunk} "
                    yield f"{chunk} "
                    # logger.info(f"Chunk: {chunk}")
                    await asyncio.sleep(0.1)
                
                # add the user query and assistant response to the chat history
                # This is done by the ChatHistoryService in the kernel.
                chat_history = self._add_to_chat_history(chat_history, query, fallback_message)
                final_response = self._final_response(message = message_accumulator, chat_history=chat_history)
                
                await asyncio.sleep(0.1)  # ensure async yield
                yield f"\n<|END_OF_RESPONSE|>\n{json.dumps(final_response)}"
                return  # 🚨 Important: do not continue to OpenAI call!
            
            result = await self.__kernel.ask(query, chat_history, kb_results, web_search_results, stream=True)
        
            async for chunk in result:
                message_accumulator += str(chunk[0])
                # logger.info(f"Chunk: {str(chunk[0])}")
                yield str(chunk[0])
                await asyncio.sleep(0.1)
            
            # add the user query and assistant response to the chat history
            # This is done by the ChatHistoryService in the kernel.
            chat_history = self._add_to_chat_history(chat_history, query, message_accumulator)
            logger.info(f"Agent Response - using RAG: {message_accumulator}")
            final_response = self._final_response(message_accumulator, kb_results, web_search_results, chat_history)
            # Yield the final JSON string to client
            yield f"\n<|END_OF_RESPONSE|>\n{json.dumps(final_response)}"
            
        except Exception as e:
            logger.error(f"Encountered Error: {e}")
            raise e
    
    def _add_to_chat_history(self, chat_history:ChatHistory, user_query:str, assistant_response:str) -> ChatHistory:
        """
        Add the user query and assistant response to the chat history.
        """
        chat_history.add_user_message(user_query)
        chat_history.add_assistant_message(assistant_response)
        return chat_history
    
    def _final_response(self, 
                        message:str, 
                        kb_results:list[Dict[str, Any] | None] = [], 
                        web_search_results: Any | Dict[str, Dict[str, Any]] = {}, 
                        chat_history:ChatHistory = None) -> dict[str, Any]:
        """
        Create the final response dictionary to be returned to the client.
        """
        return {
            "name": "George",
            "message": message,
            "kb_results": kb_results,
            "web_search_results": web_search_results,
            "chat_history": chat_history.to_prompt() if chat_history else None
        }
    
    async def _get_information_async(self, query:str, chat_history:ChatHistory):
        
        # Break down the query into smaller queries for better results
        # This is done by the QueryStructuringPlugin in the kernel.
        re_queries = await self.breakdown_query_async(query,chat_history)
        
        # re_queries, re_generate_query = await asyncio.gather(re_queries_task, re_generate_query_task)
        # logger.warning(f"Re-composed queries: {re_queries}\nRe-generated query: {re_generate_query}")
        
        # Retrieve stored knowledge base results for each re-composed query
        # This is done by the KnowledgeBaseService in the kernel.
        kb_results = await asyncio.gather(*(self.__memory_service.search_kb(query) for query in re_queries['recomposed_queries']))

        
        # Run KB search and web search in parallel
        # kb_results, web_search_results = await asyncio.gather(kb_task, web_search_task)

        # Remove duplicates using (podcast_title, time_stamp) as the unique key
        if(kb_results):
            seen = set()
            unique_kb_results = []
            for item in kb_results:
                if item:
                    key = (item.get("podcast_title"), item.get("time_stamp"))
                    if key not in seen:
                        unique_kb_results.append(item)
                        seen.add(key)
            kb_results = unique_kb_results
            logger.info(f"KB Results: {kb_results}")
            
            web_search_results = {}
            
            if len(kb_results) > 0:
                re_generate_query = await self.regenerate_query_async(query, chat_history)
                # Perform web search using the Bing web search API
                # This is done by the WebSearchEnginePlugin in the kernel.
                web_search_results = await self.__search_connector.search(re_generate_query, num_results=3)
                logger.info(f"Web Search Results: {web_search_results}")
        
        ## Convert the results to the appropriate models
        if not isinstance(web_search_results, dict):
            web_search_results = json.loads(web_search_results)
    
        return kb_results, web_search_results
            
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