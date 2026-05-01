from __future__ import annotations

import uuid

from redis.asyncio import Redis


def _refresh_token_key(token: str) -> str:
    return f"refresh:token:{token}"


def _user_tokens_key(user_id: uuid.UUID) -> str:
    """Set of all active refresh tokens for a user."""
    return f"refresh:user:{user_id}"


def _reset_token_key(token: str) -> str:
    return f"pwreset:token:{token}"


class TokenRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def store_refresh_token(
        self,
        *,
        user_id: uuid.UUID,
        token: str,
        ttl_seconds: int,
    ) -> None:
        pipe = self.redis.pipeline()
        pipe.setex(
            _refresh_token_key(token),
            ttl_seconds,
            str(user_id),
        )
        pipe.sadd(
            _user_tokens_key(user_id),
            token,
        )
        pipe.expire(
            _user_tokens_key(user_id),
            ttl_seconds,
        )
        await pipe.execute()

    async def get_user_id_for_refresh_token(self, token: str) -> uuid.UUID | None:
        value = await self.redis.get(_refresh_token_key(token))
        if value is None:
            return None
        return uuid.UUID(value)

    async def revoke_refresh_token(self, token: str) -> None:
        user_id = await self.get_user_id_for_refresh_token(token)
        pipe = self.redis.pipeline()
        pipe.delete(_refresh_token_key(token))
        if user_id is not None:
            pipe.srem(_user_tokens_key(user_id), token)
        await pipe.execute()

    async def revoke_all_refresh_tokens(self, user_id: uuid.UUID) -> None:
        user_key = _user_tokens_key(user_id)
        tokens = await self.redis.smembers(user_key)
        if not tokens:
            return
        pipe = self.redis.pipeline()
        for token in tokens:
            pipe.delete(_refresh_token_key(token))
        pipe.delete(user_key)
        await pipe.execute()

    async def store_reset_token(
        self,
        *,
        user_id: uuid.UUID,
        token: str,
        ttl_seconds: int = 3600,
    ) -> None:
        await self.redis.setex(
            _reset_token_key(token),
            ttl_seconds,
            str(user_id),
        )

    async def get_user_id_for_reset_token(self, token: str) -> uuid.UUID | None:
        value = await self.redis.get(_reset_token_key(token))
        if value is None:
            return None
        return uuid.UUID(value)

    async def revoke_reset_token(self, token: str) -> None:
        await self.redis.delete(_reset_token_key(token))
