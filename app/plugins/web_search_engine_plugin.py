from typing import TYPE_CHECKING, Annotated

from semantic_kernel.functions.kernel_function_decorator import kernel_function

from ..connectors.search_engine.connector import SearchConnectorBase

class WebSearchEnginePlugin:
    """A plugin that provides web search engine functionality.
    
    Usage:
        connector = SerpApiBingService(api_key)
        kernel.add_lugin(WebSearchEnginePlugin(connector), plugin_name="BingWebSearch")
    """
    __connector: "SearchConnectorBase"
    def __init__(self, connector: "SearchConnectorBase") -> None:
        self.__connector = connector
        
    @kernel_function(name="search", description="Performs a web search for a given query")
    async def search(
        self,
        query: Annotated[str, "The search query"],
        num_results: Annotated[int, "The number of search results to return"] = 2
    ):
        """Returns the search results of the query provided."""
        return await self.__connector.search(query,num_results)