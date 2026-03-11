from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.circle import SavingsCircle
from app.schemas.circle import CircleResponse, CreateCircleRequest, compute_end_date

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_circle(
    body: CreateCircleRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    end_date = compute_end_date(body.start_date, body.payout_count, body.frequency)

    circle = SavingsCircle(
        creator_id=user["id"],
        name=body.name,
        amount=body.amount,
        members=body.members,
        frequency=body.frequency.value,
        start_date=body.start_date,
        end_date=end_date,
        payout_count=body.payout_count,
        penalty_percent=body.penalty_percent,
        grace_period_days=body.grace_period_days,
        start_when_members=body.start_when_members,
    )
    db.add(circle)
    await db.flush()
    await db.refresh(circle)

    return {"success": True, "data": CircleResponse.model_validate(circle)}


@router.get("", status_code=status.HTTP_200_OK)
async def list_circles(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(SavingsCircle)
        .where(SavingsCircle.creator_id == user["id"])
        .order_by(SavingsCircle.created_at.desc())
    )
    circles = result.scalars().all()

    return {
        "success": True,
        "data": [CircleResponse.model_validate(c) for c in circles],
    }
