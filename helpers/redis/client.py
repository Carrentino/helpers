import aioredis
from aioredis import Redis


class RedisClient:
    def __init__(self, address: str = 'redis://localhost', minsize: int = 5, maxsize: int = 10) -> None:
        self.address = address
        self.minsize = minsize
        self.maxsize = maxsize
        self.redis = None

    async def __aenter__(self) -> Redis:
        self.redis = await aioredis.from_url(
            self.address, minsize=self.minsize, maxsize=self.maxsize
        )
        return self.redis

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()