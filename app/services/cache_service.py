"""Redis caching service."""
import json
import redis
from typing import Optional, Any
from app.core.config import get_settings
from datetime import datetime

settings = get_settings()

redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


class CacheService:
    """Service for Redis cache operations."""

    def __init__(self):
        self.client = redis_client
        self.ttl = settings.cache_ttl

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        self.client.setex(
            key,
            ttl or self.ttl,
            json.dumps(value, default=str),
        )

    def delete(self, key: str) -> None:
        """Delete a cache key."""
        self.client.delete(key)

    def flush_analytics(self) -> None:
        """Flush all analytics cache keys."""
        keys = self.client.keys("analytics:*")
        if keys:
            self.client.delete(*keys)

    def health_check(self) -> bool:
        """Check Redis connectivity."""
        try:
            return self.client.ping()
        except Exception:
            return False


def get_cache_service() -> CacheService:
    """Factory for cache service."""
    return CacheService()