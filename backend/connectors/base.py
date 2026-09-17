import httpx
import hashlib
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Optional
from connectors.cache import Cache

cache = Cache()


class BaseConnector(ABC):
    name: str = "base"
    base_url: str = ""
    auth_type: str = "none"
    default_ttl: int = 86400

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=15.0,
            headers={"User-Agent": "RadarAI/1.0"},
            follow_redirects=True,
        )

    async def close(self):
        await self.client.aclose()

    def _cache_key(self, query: dict) -> str:
        raw = json.dumps(query, sort_keys=True, default=str)
        h = hashlib.md5(raw.encode()).hexdigest()
        return f"{self.name}:{h}"

    async def cached_fetch(self, query: dict, ttl: int = None) -> Optional[dict]:
        ttl = ttl or self.default_ttl
        key = self._cache_key(query)
        cached = cache.get(key)
        if cached is not None:
            return cached
        result = await self.fetch(query)
        if result is not None:
            cache.set(key, result, ttl)
        return result

    @abstractmethod
    async def fetch(self, query: dict) -> Optional[dict]:
        raise NotImplementedError

    async def health_check(self) -> bool:
        try:
            resp = await self.client.get(self.base_url, timeout=5)
            return resp.status_code < 500
        except Exception:
            return False
