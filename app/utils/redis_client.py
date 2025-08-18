import asyncio
from typing import Optional
from redis.asyncio import Redis
from app.config import redis_url

_redis: Optional[Redis] = None
_lock = asyncio.Lock()

async def get_redis() -> Redis:
    global _redis
    async with _lock:
        if _redis is None:
            _redis = Redis.from_url(redis_url(), decode_responses=True)
    return _redis
