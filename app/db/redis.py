from __future__ import annotations

from redis.asyncio import Redis, ConnectionPool

from app.core.config import config

pool = ConnectionPool(
    host=config.redis.host,
    port=config.redis.port,
    db=config.redis.db,
    max_connections=20,
    decode_responses=True,
)


async def get_redis() -> Redis:
    return Redis(connection_pool=pool)
