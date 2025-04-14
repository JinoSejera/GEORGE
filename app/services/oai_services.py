from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding

from ..utils.get_oai_client import get_azure_oai_client
SERVICE_ID = "george"

def get_completion_service():
    return AzureChatCompletion(
        service_id=SERVICE_ID,
        async_client=get_azure_oai_client()
    )
def get_embedding_service():
    return AzureTextEmbedding(
        service_id="embedding",
        async_client=get_azure_oai_client()
    )