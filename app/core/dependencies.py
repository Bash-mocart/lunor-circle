from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import AsyncSessionLocal

_event_bus_pool: aioredis.Redis | None = None


async def get_event_bus() -> AsyncGenerator[aioredis.Redis, None]:
    global _event_bus_pool
    if _event_bus_pool is None:
        _event_bus_pool = aioredis.from_url(settings.event_bus_url, decode_responses=True)
    yield _event_bus_pool

_bearer = HTTPBearer()


def decode_token(token: str) -> dict:
    """Validate a JWT issued by lunor-auth. Raises ValueError on failure."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        raise ValueError("Invalid or expired token.")

    if payload.get("type") != "access":
        raise ValueError("Invalid token type.")

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Token missing subject.")

    return {**payload, "id": user_id, "access_token": token}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    """Validates the Bearer JWT and returns the decoded user payload."""
    try:
        return decode_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yields a DB session, committing on success and rolling back on error."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
