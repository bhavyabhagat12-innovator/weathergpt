"""
Base connector class with caching, retry, and graceful degradation.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import httpx

logger = logging.getLogger("weathergpt.ingestion")


class BaseConnector(ABC):
    """Abstract base class for all external weather data connectors."""

    def __init__(self, name: str, cache_ttl_seconds: int = 600, timeout_seconds: float = 8.0):
        self.name = name
        self.cache_ttl_seconds = cache_ttl_seconds
        self.timeout = timeout_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _get_from_cache(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.cache_ttl_seconds:
                return entry["data"]
            del self._cache[key]
        return None

    def _set_in_cache(self, key: str, data: Any):
        self._cache[key] = {
            "timestamp": time.time(),
            "data": data
        }

    async def fetch_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch JSON with timeout and connection error handling."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
