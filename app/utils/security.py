import os
from dotenv import load_dotenv

from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
import logging

# Load environment variables from a .env file
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)

# Retrieve API keys from environment variables; fallback to empty string if not set
API_KEYS = [os.getenv("API_KEY_1", ""), os.getenv("API_KEY_2", "")]
API_KEY_NAME = "X-API-Key"

# Define the API key header expected in requests
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Dependency function to validate the API key from the request header
async def get_api_key(api_key: str = Security(api_key_header)):
    try:
        # Check if the provided API key is in the list of allowed keys
        if api_key in API_KEYS and api_key:
            return api_key
        logger.warning(f"Unauthorized API key attempt: {api_key}")
        # Raise an HTTP 403 error if the API key is invalid or missing
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Could not validate API key",
        )
    except Exception as e:
        logger.error(f"Error during API key validation: {e}")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="API key validation error",
        )