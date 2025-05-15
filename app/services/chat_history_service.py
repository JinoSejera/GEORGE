import logging

from semantic_kernel.contents import ChatHistory

logger = logging.getLogger(__name__)

class ChatHistoryService:
    """
    Service for managing chat history operations.
    """
    
    @staticmethod
    def load_chat_history(history:str)->ChatHistory:
        """
        Load chat history from a rendered prompt string.

        Args:
            history (str): The rendered prompt representing chat history.

        Returns:
            ChatHistory: The loaded chat history object.
        """
        return ChatHistory.from_rendered_prompt(history)
    
    @staticmethod
    def get_chat_history(chat_history: ChatHistory)->str:
        """
        Convert a ChatHistory object to a prompt string.

        Args:
            chat_history (ChatHistory): The chat history object.

        Returns:
            str: The prompt string representation.
        """
        return ChatHistory.to_prompt(chat_history)
    
    @staticmethod
    def initialize_chat()->ChatHistory:
        """
        Initialize a new chat history.

        Returns:
            ChatHistory: A new chat history object.
        """
        return ChatHistory()