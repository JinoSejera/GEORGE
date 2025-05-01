import os
from typing import Any
import logging
import re
import json

import serpapi
from .connector import SearchConnectorBase
from semantic_kernel.exceptions import ServiceInvalidRequestError

logger = logging.getLogger(__name__)

class BingSerApiConnector(SearchConnectorBase):
    """A Search engine connector that uses Serpapi to perform a Bing web search."""
    
    __api_key: str
    # __client: serpapi.Client
    def __init__(self, api_key:str | None = None) -> None:
        """_summary_

        Args:
            api_key (str | None, optional): The Serpapi API Key,.
        """
        if not api_key:
            from dotenv import load_dotenv
            load_dotenv()
            self.__api_key = os.getenv("SERPAPI_API_KEY") or (lambda:(_ for _ in ()).throw(ValueError("SERPAPI_API_KEY is not set")))()
        else:
            self.__api_key = api_key
            
        # self.__client = serpapi.Client(api_key=self.__api_key)
        
    async def search(self, query: str, num_results: int = 2) -> dict[str, dict[str, Any]]:
        """Returns the search results of the query provided by pinging the Bing web search API."""
        if not query:
            raise ServiceInvalidRequestError("query cannot be 'None' or empty.")

        if num_results <= 0:
            raise ServiceInvalidRequestError("num_results value must be greater than 0.")
        if num_results >= 50:
            raise ServiceInvalidRequestError("num_results value must be less than 50.")
        
        logger.info(
            f"Received request for bing web search with \
                params:\nquery: {query}\nnum_results: {num_results}"
        )
        
        params = {
            "engine": "bing",
            "q": query,
            "api_key": self.__api_key,
        }
        
        search_result = serpapi.search(params=params)
        # results = search.get_dict()
        # logger.warning(f"search_result: {search_result}")
        references = [
            {
                "no": index,
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet")
            }
            for index, result in enumerate(search_result.get("organic_results", [])[:num_results], start=1) 
        ]
        
        answer = " ".join(f"{self.__clean_snippet(ref['snippet'])}[{ref['no']}]" for ref in references)
        
        # logger.debug(f"answer: {answer}\nreferences: {references}")
        return json.dumps({
            "organic_result": {
                "answer": answer,
                "references": references
            }
        })
        
    def __clean_snippet(self, snippet):
        return re.sub(r"\[\d+\](\s*\.)?", "", snippet).strip()