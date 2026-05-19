import time
from functools import wraps


class InMemoryCache:
    """
    Simple in-memory cache with TTL.
    Keyed by endpoint + query params.
    Invalidated explicitly after each scheduler run.
    
    No Redis, no LRU eviction — a dict with timestamps is the right
    trade-off for this project's scale (~50-200 articles, <100 concurrent users).
    """

    def __init__(self, ttl_seconds: int = 300):
        self._cache: dict[str, dict] = {}
        self._ttl = ttl_seconds

    def get(self, key: str):
        """Get cached value if it exists and hasn't expired."""
        entry = self._cache.get(key)
        if entry is None:
            return None
        if time.time() - entry["timestamp"] > self._ttl:
            del self._cache[key]
            return None
        return entry["data"]

    def set(self, key: str, data):
        """Cache a value with the current timestamp."""
        self._cache[key] = {
            "data": data,
            "timestamp": time.time(),
        }

    def clear(self):
        """Clear entire cache. Called after scheduler runs."""
        self._cache.clear()
        print("[Cache] Cache cleared")

    @property
    def size(self) -> int:
        return len(self._cache)


# Singleton cache instance
cache = InMemoryCache()
