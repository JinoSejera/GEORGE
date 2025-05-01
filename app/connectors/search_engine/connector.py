# Copyright (c) Microsoft. All rights reserved.

from abc import ABC, abstractmethod
from typing import Any, Dict

class SearchConnectorBase(ABC):
    """Base class for search engine connectors."""

    @abstractmethod
    async def search(self, query: str, num_results: int = 1) -> Dict[str, Dict[str, Any]]:
        """Returns the search results of the query provided by pinging the search engine API."""
        pass
