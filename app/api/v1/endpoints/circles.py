import uuid
from collections import defaultdict

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, get_event_bus
from app.events.publisher import EventPublisher
from app.models.circle import SavingsCircle
from app.models.member import CircleMember
from app.schemas.circle import CircleResponse, CreateCircleRequest, compute_end_date

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_circle(
    body: CreateCircleRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
    event_bus: aioredis.Redis = Depends(get_event_bus),
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

    publisher = EventPublisher(event_bus)
    await publisher.circle_created(circle)
    await publisher.member_joined(circle.id, user["id"])

    response = CircleResponse.model_validate(circle)
    response.joined_count = 1
    response.member_user_ids = [user["id"]]

    return {"success": True, "data": response}


@router.get("", status_code=status.HTTP_200_OK)
async def list_circles(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    # Fetch all circles where the user has an active membership
    # (creators are added as members at creation time, so this covers both)
    my_memberships = await db.execute(
        select(CircleMember.circle_id)
        .where(CircleMember.user_id == user["id"])
        .where(CircleMember.status == "active")
    )
    circle_ids = [row[0] for row in my_memberships.all()]

    circles: list[SavingsCircle] = []
    members_by_circle: dict[str, list[str]] = defaultdict(list)

    if circle_ids:
        circles_result = await db.execute(
            select(SavingsCircle)
            .where(SavingsCircle.id.in_(circle_ids))
            .order_by(SavingsCircle.created_at.desc())
        )
        circles = circles_result.scalars().all()

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


@router.get("/by-code/{invite_code}", status_code=status.HTTP_200_OK)
async def get_circle_by_code(
    invite_code: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(SavingsCircle).where(SavingsCircle.invite_code == invite_code.upper())
    )
    circle = result.scalar_one_or_none()
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")

    members_result = await db.execute(
        select(CircleMember)
        .where(CircleMember.circle_id == circle.id)
        .where(CircleMember.status == "active")
    )
    user_ids = [m.user_id for m in members_result.scalars().all()]

    response = CircleResponse.model_validate(circle)
    response.joined_count = len(user_ids)
    response.member_user_ids = user_ids

    return {"success": True, "data": response}


@router.post("/by-code/{invite_code}/join", status_code=status.HTTP_200_OK)
async def join_circle_by_code(
    invite_code: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
    event_bus: aioredis.Redis = Depends(get_event_bus),
):
    result = await db.execute(
        select(SavingsCircle).where(SavingsCircle.invite_code == invite_code.upper())
    )
    circle = result.scalar_one_or_none()
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")

    members_result = await db.execute(
        select(CircleMember)
        .where(CircleMember.circle_id == circle.id)
        .where(CircleMember.status == "active")
    )
    active_members = members_result.scalars().all()
    user_ids = [m.user_id for m in active_members]

    if user["id"] in user_ids:
        raise HTTPException(status_code=409, detail="Already a member of this circle")

    if len(user_ids) >= circle.members:
        raise HTTPException(status_code=409, detail="Circle is full")

    member = CircleMember(
        id=str(uuid.uuid4()),
        circle_id=circle.id,
        user_id=user["id"],
    )
    db.add(member)
    await db.commit()

    await EventPublisher(event_bus).member_joined(circle.id, user["id"])

    user_ids.append(user["id"])
    response = CircleResponse.model_validate(circle)
    response.joined_count = len(user_ids)
    response.member_user_ids = user_ids

    return {"success": True, "data": response}


@router.get("/{circle_id}", status_code=status.HTTP_200_OK)
async def get_circle(
    circle_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(SavingsCircle).where(SavingsCircle.id == circle_id)
    )
    circle = result.scalar_one_or_none()
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")

    members_result = await db.execute(
        select(CircleMember)
        .where(CircleMember.circle_id == circle_id)
        .where(CircleMember.status == "active")
    )
    user_ids = [m.user_id for m in members_result.scalars().all()]

    response = CircleResponse.model_validate(circle)
    response.joined_count = len(user_ids)
    response.member_user_ids = user_ids

    return {"success": True, "data": response}


@router.post("/{circle_id}/join", status_code=status.HTTP_200_OK)
async def join_circle(
    circle_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
    event_bus: aioredis.Redis = Depends(get_event_bus),
):
    result = await db.execute(
        select(SavingsCircle).where(SavingsCircle.id == circle_id)
    )
    circle = result.scalar_one_or_none()
    if not circle:
        raise HTTPException(status_code=404, detail="Circle not found")

    members_result = await db.execute(
        select(CircleMember)
        .where(CircleMember.circle_id == circle_id)
        .where(CircleMember.status == "active")
    )
    active_members = members_result.scalars().all()
    user_ids = [m.user_id for m in active_members]

    if user["id"] in user_ids:
        raise HTTPException(status_code=409, detail="Already a member of this circle")

    if len(user_ids) >= circle.members:
        raise HTTPException(status_code=409, detail="Circle is full")

    member = CircleMember(
        id=str(uuid.uuid4()),
        circle_id=circle_id,
        user_id=user["id"],
    )
    db.add(member)
    await db.commit()

    await EventPublisher(event_bus).member_joined(circle_id, user["id"])

    user_ids.append(user["id"])
    response = CircleResponse.model_validate(circle)
    response.joined_count = len(user_ids)
    response.member_user_ids = user_ids

    return {"success": True, "data": response}
