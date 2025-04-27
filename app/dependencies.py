import logging

from fastapi import Depends

# Import service and repository classes used for dependency injection
from .services.george_qa_service import GeorgeQAService
from .repository.kernel_repository import KernelRepository
from .repository.knowledge_base_repository import KnowledgeBaseRepository
from .services.chat_history_service import ChatHistoryService
from .services.knowledge_base_service import KnowledgeBaseService
from .connectors.search_engine.bing_serapi_connector import BingSerApiConnector
logger = logging.getLogger(__name__)

# Provides an instance of KernelRepository for dependency injection
def get_kernel_repository():
    return KernelRepository()

# Provides an instance of KnowledgeBaseRepository for dependency injection
def get_knowledge_base_repository():
    return KnowledgeBaseRepository()

# Provides an instance of BingSerApiConnector for dependency injection
def get_bing_serapi_connector():
    return BingSerApiConnector()

# Provides an instance of KnowledgeBaseService, initialized with a KnowledgeBaseRepository
def get_knowledge_base_service(kb: KnowledgeBaseRepository = Depends(get_knowledge_base_repository)):
    logger.info("Initializing George Knowledge Base Service")
    return KnowledgeBaseService(kb)

# Provides an instance of GeorgeQAService, initialized with a KernelRepository
def get_george_ask_service(kernel: KernelRepository = Depends(get_kernel_repository),
                           knowledge_base: KnowledgeBaseRepository = Depends(get_knowledge_base_service),
                           search_connector: BingSerApiConnector = Depends(get_bing_serapi_connector)):
    logger.info("Initializing George Q and A Service")
    return GeorgeQAService(kernel,knowledge_base,search_connector)
    
# Provides an instance of ChatHistoryService for dependency injection
def get_chat_history():
    return ChatHistoryService()

# Provides an instance of KnowledgeBaseService with a new KnowledgeBaseRepository
def get_memory_service():
    return KnowledgeBaseService(KnowledgeBaseRepository())