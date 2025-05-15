from abc import abstractmethod, ABC
from typing import AsyncGenerator, Iterable, Optional, Any, Dict

from semantic_kernel import Kernel
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions.function_result import FunctionResult
from semantic_kernel.contents.streaming_content_mixin import StreamingContentMixin



class KernelRepositoryBase(ABC):
    @abstractmethod
    def get_kernel(self)->Kernel:
        """
        Returns the kernel instance.
        """
        pass
    
    @abstractmethod
    async def ask_async(
        self, 
        query: str,
        kb_results:Iterable[Optional[Dict[str, Any]]] | None, 
        web_results:Dict[str, Dict[str, Any]] | None,
        stream:bool = False
    ) -> AsyncGenerator[list[StreamingContentMixin] | FunctionResult | list[FunctionResult], Any] | str:
        """
        Asynchronously asks a question to the kernel and returns the response.

        Args:
            query (str): The user query.
            kb_results (Iterable[Optional[Dict[str, Any]]] | None): Knowledge base results.
            web_results (Dict[str, Dict[str, Any]] | None): Web search results.
            stream (bool, optional): Whether to stream the response. Defaults to False.

        Returns:
            AsyncGenerator or str: The response from the kernel.
        """
        pass
    
    @abstractmethod
    async def breakdown_query_async(self, query:str, chat_history: ChatHistory)->str:
        """
        Asynchronously breaks down a query into smaller sub-queries.

        Args:
            query (str): The user query.
            chat_history (ChatHistory): The conversation history.

        Returns:
            str: The breakdown result.
        """
        pass
    
    @abstractmethod
    async def regenerate_query_async(self, query:str, chat_history: ChatHistory)->str:
        """
        Asynchronously regenerates the query based on the conversation history.

        Args:
            query (str): The user query.
            chat_history (ChatHistory): The conversation history.

        Returns:
            str: The regenerated query.
        """
        pass
    
    @abstractmethod
    async def check_history_async(self, query:str, chat_history: ChatHistory) -> str:
        """
        Asynchronously checks the conversation history for relevant context.

        Args:
            query (str): The user query.
            chat_history (ChatHistory): The conversation history.

        Returns:
            str: The result of the history check.
        """
        pass