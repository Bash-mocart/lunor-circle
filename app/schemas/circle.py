import logging
from datetime import date, datetime
from enum import Enum

import httpx
import redis.asyncio as aioredis
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field, model_validator

from app.config import settings

logger = logging.getLogger(__name__)


class Frequency(str, Enum):
    daily = "daily"
    weekly = "weekly"
    bi_weekly = "bi-weekly"
    monthly = "monthly"
    quarterly = "quarterly"


def compute_end_date(start: date, payout_count: int, frequency: Frequency) -> date:
    """Compute end date server-side. Never accept end_date from the client."""
    intervals = {
        Frequency.daily:     relativedelta(days=payout_count),
        Frequency.weekly:    relativedelta(weeks=payout_count),
        Frequency.bi_weekly: relativedelta(weeks=payout_count * 2),
        Frequency.monthly:   relativedelta(months=payout_count),
        Frequency.quarterly: relativedelta(months=payout_count * 3),
    }
    return start + intervals[frequency]


async def get_matrix_room_ids(
    circle_ids: list[str],
    redis: aioredis.Redis,
) -> dict[str, str | None]:
    """
    Return circle_id → matrix_room_id for the given IDs.
    Checks Redis cache first (no TTL — room_id is immutable once created).
    Falls back to lunor-matrix internal API for cache misses.
    """
    if not circle_ids:
        return {}

    cache_keys = [f"matrix_room:{cid}" for cid in circle_ids]
    cached_values = await redis.mget(*cache_keys)

    result: dict[str, str | None] = {}
    missing: list[str] = []

    for circle_id, cached in zip(circle_ids, cached_values):
        if cached:
            result[circle_id] = cached
        else:
            result[circle_id] = None
            missing.append(circle_id)

    if missing and settings.lunor_matrix_url:
        async with httpx.AsyncClient(timeout=5) as client:
            for circle_id in missing:
                try:
                    resp = await client.get(
                        f"{settings.lunor_matrix_url}/internal/matrix/room/{circle_id}"
                    )
                    if resp.status_code == 200:
                        room_id = resp.json()["matrix_room_id"]
                        result[circle_id] = room_id
                        await redis.set(f"matrix_room:{circle_id}", room_id)
                except Exception:
                    logger.warning("Could not fetch matrix_room_id for circle %s", circle_id)

    return result


class CreateCircleRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    amount: float = Field(gt=0)
    members: int = Field(ge=2)
    frequency: Frequency
    start_date: date
    payout_count: int = Field(ge=1)
    penalty_percent: float = Field(default=0, ge=0, le=100)
    grace_period_days: int = Field(default=0, ge=0)
    start_when_members: bool = False

    @model_validator(mode="after")
    def start_date_not_in_past(self) -> "CreateCircleRequest":
        if self.start_date < date.today():
            raise ValueError("start_date must be today or a future date")
        return self


class CircleResponse(BaseModel):
    id: str
    name: str
    amount: float
    members: int
    frequency: str
    start_date: date
    end_date: date
    payout_count: int
    penalty_percent: float
    grace_period_days: int
    start_when_members: bool
    status: str
    invite_code: str | None = None
    created_at: datetime
    joined_count: int = 0
    member_user_ids: list[str] = []
    matrix_room_id: str | None = None

    model_config = {"from_attributes": True}
