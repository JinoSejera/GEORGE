from abc import abstractmethod, ABC
from typing import Iterable, Optional, Any, Dict

from semantic_kernel import Kernel
from semantic_kernel.contents import ChatHistory

from ..models.knowledge_base_model import PodCastKnowledgeBaseModel
from ..models.web_search_result_model import WebSearchResult


class KernelRepositoryBase(ABC):
    @abstractmethod
    def get_kernel(self)->Kernel:
        """
        Get the kernel instance.
        """
        pass
    @abstractmethod
    async def ask(
        self, 
        query: str, 
        chat_history: ChatHistory, 
        kb_results:Iterable[Optional[Dict[str, Any]]] | None, 
        web_results:Dict[str, Dict[str, Any]] | None) -> str:
        """
        Ask a question to the kernel and get the response.
        """
        pass

    @abstractmethod
    async def breakdown_query(self, query:str, chat_history: ChatHistory)->str:
        """
        Breaking down query into smaller queries.
        """
        pass
    
    @abstractmethod
    async def regenerate_query(self, query:str, chat_history: ChatHistory)->str:
        """
        Regenerate the query based on the conversation history.
        """
        pass
    