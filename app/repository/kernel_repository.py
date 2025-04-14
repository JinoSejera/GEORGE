import os
import logging
from pathlib import Path

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
from semantic_kernel.contents import ChatHistory
from semantic_kernel.core_plugins import ConversationSummaryPlugin
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding

from ..utils.singleton_decorator import singleton
from ..utils.prompt_template_config import Config, get_prompt_template_config, get_conversation_summarizer_config
from ..services.oai_services import get_completion_service, get_embedding_service

current_path = Path(__file__).resolve().parent
plugin_dir = current_path / "../plugins/"

logger = logging.getLogger(__name__)

@singleton
class KernelRepository:
    """
    Singleton class to manage the kernel instance.a
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
        self.__kernel.add_plugin(ConversationSummaryPlugin(prompt_template_config=get_conversation_summarizer_config()),"summarizer")
        self.__orchestrator = self.__kernel.add_plugin(parent_directory=plugin_dir, plugin_name="GeorgeQAPlugin")
        
        
        logger.info(self.__kernel.plugins)
    def get_kernel(self):
        """
        Get the kernel instance.
        """
        return self.__kernel
    
    def get_embedding_service(self)->AzureTextEmbedding:
        return self.__embedding_service
    
    async def ask(self, query: str, chat_history: ChatHistory, kb_result:dict):
        """
        Ask a question to the kernel and get the response.
        """
        try:
            result = await self.__kernel.invoke(self.__orchestrator['QA'], KernelArguments(query=query, history=str(chat_history), knowledge_base=kb_result))
            
            return str(result)
        except Exception as e:
            raise e