from datetime import date, datetime
from enum import Enum
from typing import Literal

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field, model_validator


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
    created_at: datetime

    model_config = {"from_attributes": True}
