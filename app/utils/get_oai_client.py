import os
import logging
from dotenv import load_dotenv

from openai import AsyncAzureOpenAI
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()
logger = logging.getLogger(__name__)
azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT') or (lambda:(_ for _ in ()).throw(ValueError("AZURE_OPENAI_ENDPOINT is not set")))()
azure_openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION') or (lambda:(_ for _ in ()).throw(ValueError("AZURE_OPENAI_API_VERSION is not set")))()
        
def get_azure_oai_client():
    try:
        __token_provider = get_bearer_token_provider(DefaultAzureCredential(),'https://cognitiveservices.azure.com/.default')
        __async_client = AsyncAzureOpenAI(azure_endpoint=azure_openai_endpoint,
                    azure_ad_token_provider=__token_provider,
                    api_version=azure_openai_api_version)
        logger.info(f"Azure OpenAI client created successfully with endpoint: {azure_openai_endpoint} and API version: {azure_openai_api_version}")
        return __async_client
    except Exception as e:
        logger.error(f"Error creating Azure OpenAI client: {e}")
        raise