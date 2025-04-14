import logging

from semantic_kernel.contents import ChatHistory

logger = logging.getLogger(__name__)

class ChatHistoryService:
    
    @staticmethod
    def load_chat_history(history:str)->ChatHistory:
        return ChatHistory.from_rendered_prompt(history)
    
    @staticmethod
    def get_chat_history(chat_history: ChatHistory)->str:
        return ChatHistory.to_prompt(chat_history)
    
    @staticmethod
    def initialize_chat()->ChatHistory:
        return ChatHistory()