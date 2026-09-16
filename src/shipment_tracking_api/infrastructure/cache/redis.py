import json

from redis.asyncio import Redis


# Basic class with Redis methods
class RedisCacheBackend:
    def __init__(self, redis: Redis, cache_ttl_seconds: int | None = None):
        self._redis = redis
        self.cache_ttl_seconds = cache_ttl_seconds

    @classmethod
    def from_url(
        cls, redis_url: str, cache_ttl_seconds: int | None = None
    ) -> "RedisCacheBackend":
        redis = Redis.from_url(redis_url, decode_responses=True)
        return cls(redis, cache_ttl_seconds)

    async def close(self) -> None:
        await self._redis.aclose()

    async def ping(self) -> bool:
        return await self._redis.ping()

    async def set(self, key: str, value: dict) -> None:
        await self._redis.set(key, json.dumps(value), ex=self.cache_ttl_seconds)

    async def get(self, key: str) -> dict | None:
        value = await self._redis.get(key)
        if value is not None:
            return json.loads(value)
        return None

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)
