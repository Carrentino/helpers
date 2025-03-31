import redis.asyncio as redis
from redis.asyncio import Redis


class RedisClient:
    def __init__(self, address: str = 'redis_client://localhost', db: int = 0) -> None:
        self.address = address
        self.db = db
        self.redis = None

    async def __aenter__(self) -> Redis:
        self.redis = redis.from_url(
            self.address, db=self.db, decode_responses=True
        )
        return self.redis

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self.redis:
            await self.redis.close()