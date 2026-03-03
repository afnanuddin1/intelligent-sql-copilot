import json
import redis.asyncio as aioredis
from app.config import get_settings

settings = get_settings()


class RedisService:
    def __init__(self):
        self.client = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True,
        )

    async def get(self, key: str) -> dict | None:
        val = await self.client.get(key)
        return json.loads(val) if val else None

    async def set(self, key: str, value: dict, ttl: int):
        await self.client.setex(key, ttl, json.dumps(value, default=str))

    async def delete_pattern(self, pattern: str):
        keys = await self.client.keys(pattern)
        if keys:
            await self.client.delete(*keys)

    async def ping(self) -> bool:
        try:
            return await self.client.ping()
        except Exception:
            return False


redis_service = RedisService()
