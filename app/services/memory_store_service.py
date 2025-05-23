import os
import logging
from dotenv import load_dotenv

from azure.identity import ClientSecretCredential
from semantic_kernel.connectors.memory.azure_cognitive_search import AzureCognitiveSearchMemoryStore


load_dotenv()
VECTOR_SIZE = 1536

search_enpoint = os.getenv('SEARCH_ENDPOINT') or (lambda:(_ for _ in ()).throw(ValueError("SEARCH_ENDPOINT is not set")))()
search_key = os.getenv('SEARCH_KEY') or (lambda:(_ for _ in ()).throw(ValueError("SEARCH_KEY is not set")))()


logger = logging.getLogger(__name__)


def get_memory_store():
    """
    Initialize and return an Azure Cognitive Search memory store instance.

    Returns:
        AzureCognitiveSearchMemoryStore: The initialized memory store.

    Raises:
        Exception: If initialization fails.
    """
    logger.info("Initializing Knowledge Base")
    try:
        return AzureCognitiveSearchMemoryStore(
            vector_size=VECTOR_SIZE,
            search_endpoint=search_enpoint,
            admin_key=search_key
        )
    except Exception as e:
        logger.error(f"Error encountered on initializing knowledge base: {e}")
        raise e