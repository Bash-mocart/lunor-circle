import uuid
from collections import defaultdict

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.circle import SavingsCircle
from app.models.member import CircleMember
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

    member = CircleMember(
        id=str(uuid.uuid4()),
        circle_id=circle.id,
        user_id=user["id"],
    )
    db.add(member)
    await db.commit()

    response = CircleResponse.model_validate(circle)
    response.joined_count = 1
    response.member_user_ids = [user["id"]]

    return {"success": True, "data": response}


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

    circle_ids = [c.id for c in circles]

    members_by_circle: dict[str, list[str]] = defaultdict(list)
    if circle_ids:
        members_result = await db.execute(
            select(CircleMember)
            .where(CircleMember.circle_id.in_(circle_ids))
            .where(CircleMember.status == "active")
        )
        for m in members_result.scalars().all():
            members_by_circle[m.circle_id].append(m.user_id)

    data = []
    for c in circles:
        user_ids = members_by_circle.get(c.id, [])
        response = CircleResponse.model_validate(c)
        response.joined_count = len(user_ids)
        response.member_user_ids = user_ids
        data.append(response)

    return {"success": True, "data": data}
