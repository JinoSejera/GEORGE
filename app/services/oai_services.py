import logging

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding

from ..utils.get_oai_client import get_azure_oai_client
SERVICE_ID = "george"

logger = logging.getLogger(__name__)

def get_completion_service():
    """
    Get the Azure Chat Completion service instance.

    Returns:
        AzureChatCompletion: The chat completion service.
    """
    logger.info("Getting Azure Chat Completion Service.")
    return AzureChatCompletion(
        service_id=SERVICE_ID,
        async_client=get_azure_oai_client()
    )

def get_embedding_service():
    """
    Get the Azure Text Embedding service instance.

    Returns:
        AzureTextEmbedding: The text embedding service.
    """
    logger.info("Getting Azure Text Embedding Service.")
    return AzureTextEmbedding(
        service_id="embedding",
        async_client=get_azure_oai_client()
    )