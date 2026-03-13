import uuid
from datetime import date, datetime

from nanoid import generate
from sqlalchemy import Boolean, Date, DateTime, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_INVITE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O/1/I/L


def _generate_invite_code() -> str:
    return generate(_INVITE_ALPHABET, 8)


class SavingsCircle(Base):
    __tablename__ = "savings_circles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    creator_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    members: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    payout_count: Mapped[int] = mapped_column(Integer, nullable=False)
    penalty_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    grace_period_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    start_when_members: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    invite_code: Mapped[str | None] = mapped_column(
        String(8), unique=True, nullable=True, index=True,
        default=_generate_invite_code,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("ix_savings_circles_creator_id", "creator_id"),
    )
