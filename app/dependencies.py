import logging

from fastapi import Depends

from .services.george_qa_service import GeorgeQAService
from .repository.kernel_repository import KernelRepository
from .repository.knowledge_base_repository import KnowledgeBaseRepository
from .services.chat_history_service import ChatHistoryService
from .services.knowledge_base_service import KnowledgeBaseService

logger = logging.getLogger(__name__)

def get_kernel_repository():
    return KernelRepository()

def get_knowledge_base_repository():
    return KnowledgeBaseRepository()

def get_george_ask_service(kernel: KernelRepository = Depends(get_kernel_repository)):
    logger.info("Initializing George Q and A Service")
    return GeorgeQAService(kernel)

def get_knowledge_base_service(kb: KnowledgeBaseRepository = Depends(get_knowledge_base_repository)):
    return KnowledgeBaseService(kb)
    
def get_chat_history():
    return ChatHistoryService()