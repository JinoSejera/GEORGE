import logging
import json

from semantic_kernel.contents import ChatHistory

from ..repository.kernel_repository import KernelRepository


logger = logging.getLogger(__name__)

class GeorgeQAService:
    def __init__(self, kernel: KernelRepository):
        self.__kernel = kernel
        
    async def ask_george_async(self, query:str, chat_history:ChatHistory, kb_results:list[dict]):
        try:
            response = await self.__kernel.ask(query, chat_history, kb_results)
            return response
        except Exception as e:
            logger.error(f"Encountered Error: {e}")
            raise e
    
    async def recompose_query_async(self, query:str):
        try:
            response = json.loads((await self.__kernel.recompose_query(query)))
            return response
        except Exception as e:
            logger.error(f"Encountered Error: {e}")
            raise e
        