from typing import AsyncGenerator, Iterable, Optional, Any, Dict
import logging
from pathlib import Path
import json

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
from semantic_kernel.contents import ChatHistory
from semantic_kernel.core_plugins import ConversationSummaryPlugin, TimePlugin
from semantic_kernel.functions.function_result import FunctionResult
from semantic_kernel.contents.streaming_content_mixin import StreamingContentMixin

from ..utils.singleton_decorator import singleton
from ..utils.prompt_template_config import Config, get_prompt_template_config
from ..services.oai_services import get_completion_service, get_embedding_service
from ..contract.kernel_repository_base import KernelRepositoryBase
current_path = Path(__file__).resolve().parent
plugin_dir = current_path / "../plugins/"

logger = logging.getLogger(__name__)

@singleton
class KernelRepository(KernelRepositoryBase):
    """
    Singleton class to manage the kernel instance.
    """
    def __init__(self):
        self.__kernel = Kernel()
        
        # add completion service
        self.__embedding_service = get_embedding_service()
        
        self.__kernel.add_service(
            service=get_completion_service()
        )
        self.__kernel.add_service(
            service=self.__embedding_service
            )
        
        # load plugins
        self.__kernel.add_plugin(TimePlugin(), plugin_name="time")
        self.__kernel.add_plugin(ConversationSummaryPlugin(prompt_template_config=get_prompt_template_config(Config.CONVERSATION_SUMMARIZER)),"summarizer")
        self.__orchestrator = self.__kernel.add_plugin(parent_directory=plugin_dir, plugin_name="GeorgeQAPlugin")
        self.__query_plugin = self.__kernel.add_plugin(parent_directory=plugin_dir, plugin_name="QueryStructuringPlugin")
        
    def get_kernel(self):
        """
        Get the kernel instance.
        """
        return self.__kernel
    
    async def ask_async(
        self, 
        query: str,
        kb_results:Iterable[Optional[Dict[str, Any]]] | None, 
        web_results:Dict[str, Dict[str, Any]] | None,
        stream:bool = False)->AsyncGenerator[list[StreamingContentMixin] | FunctionResult | list[FunctionResult], Any] | str:
        """
        Ask a question to the kernel and get the response.
        """
        try:
            args = KernelArguments(query=query,
                                   knowledge_base=kb_results,
                                   web_search=web_results)
            if stream:
                return self.__ask_stream_async(args)
            
            return str(await self.__ask_async(args))
        
        except Exception as e:
            raise e
        
    async def breakdown_query_async(self, query:str, chat_history: ChatHistory) -> str:
        """
        Breaking down query into smaller queries.
        """
        try:
            args = KernelArguments()
            args["query"] = query
            args["history"] = chat_history
            result = await self.__breakdown_query_async(args)
            return str(result)
        except Exception as e:
            raise e
    
    async def regenerate_query_async(self, query:str, chat_history: ChatHistory) -> str:
        """
        Regenerate the query based on the conversation history.
        """
        try:
            result = await self.__regenerate_query_async(KernelArguments(query=query,
                                   history=chat_history))
            return str(result)
        except Exception as e:
            raise e
        
    async def check_history_async(self, query:str, chat_history: ChatHistory) -> str:
        """
        Check the conversation history.
        """
        try:
            args = KernelArguments()
            args["history"] = chat_history
            args["query"] = query
            result = await self.__check_history_async(args)
            return str(result)
        except Exception as e:
            raise e
    async def __check_history_async(self, args: KernelArguments) -> FunctionResult:
        """
        Asynchronously checks the conversation history using the orchestrator plugin.

        Args:
            args (KernelArguments): Arguments containing history and query.

        Returns:
            FunctionResult: The result of the history check.
        """
        try:
            return await self.__kernel.invoke(self.__orchestrator['CheckHistory'], args)
        except Exception as e:
            raise e
    
    async def __regenerate_query_async(self, args: KernelArguments) -> FunctionResult:
        """
        Asynchronously regenerates the query using the QueryStructuringPlugin.

        Args:
            args (KernelArguments): Arguments containing query and history.

        Returns:
            FunctionResult: The regenerated query result.
        """
        try:
            return await self.__kernel.invoke(self.__query_plugin['RegenerateQuery'], args)
        except Exception as e:
            raise e
    
    async def __breakdown_query_async(self, args: KernelArguments) -> FunctionResult:
        """
        Asynchronously breaks down the query into smaller queries using the QueryStructuringPlugin.

        Args:
            args (KernelArguments): Arguments containing query and history.

        Returns:
            FunctionResult: The breakdown result.
        """
        try:
            return await self.__kernel.invoke(self.__query_plugin['BreakDownQuery'], args)
        except Exception as e:
            raise e
    
    async def __ask_async(
        self, 
        args: "KernelArguments") -> FunctionResult:
        try:
            return await self.__kernel.invoke(self.__orchestrator['QA'],args)
        except Exception as e:
            raise e

    def __ask_stream_async(
        self, 
        args: "KernelArguments") -> AsyncGenerator[list["StreamingContentMixin"] | FunctionResult | list[FunctionResult], Any]:
        try:
            return self.__kernel.invoke_stream(self.__orchestrator['QA'],args)
        except Exception as e:
            raise e