from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI

from app.api.v1.router import router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await aioredis.from_url(settings.redis_url, decode_responses=True)
    yield
    await app.state.redis.aclose()


app = FastAPI(
    title="Lunor Circle",
    version="0.1.0",
    description="Savings circles service",
    lifespan=lifespan,
)

app.include_router(router)
