import logging

from semantic_kernel.contents import ChatHistory

from ..repository.kernel_repository import KernelRepository


logger = logging.getLogger(__name__)

class GeorgeQAService:
    def __init__(self, kernel: KernelRepository):
        self.__kernel = kernel
        
    async def ask_george(self, query:str, chat_history:ChatHistory, kb_result:dict):
        try:
            response = await self.__kernel.ask(query, chat_history, kb_result)
            return response
        except Exception as e:
            logger.error(f"Encountered Error: {e}")
            raise e
        