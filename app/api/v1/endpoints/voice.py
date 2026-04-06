from datetime import timedelta

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, status
from livekit.api import AccessToken, VideoGrants
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.dependencies import get_current_user, get_db, get_redis
from app.models.circle import SavingsCircle
from app.models.member import CircleMember
from app.schemas.circle import get_matrix_room_ids

router = APIRouter()


@router.post("/circles/{circle_id}/voice-token")
async def get_voice_token(
    circle_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
    redis: aioredis.Redis = Depends(get_redis),
):
    """
    Returns a LiveKit access token for the voice room tied to this circle.
    The LiveKit room name is the circle's matrix_room_id (stable, already
    known to the client). Requires the caller to be an active member.
    """
    # Verify circle exists
    result = await db.execute(
        select(SavingsCircle).where(SavingsCircle.id == circle_id)
    )
    circle = result.scalar_one_or_none()
    if not circle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Circle not found")

    # Verify the user is an active member
    membership = await db.execute(
        select(CircleMember)
        .where(CircleMember.circle_id == circle_id)
        .where(CircleMember.user_id == user["id"])
        .where(CircleMember.status == "active")
    )
    if not membership.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this circle",
        )

    # Resolve the matrix_room_id — used as the LiveKit room name
    room_ids = await get_matrix_room_ids([circle_id], redis)
    matrix_room_id = room_ids.get(circle_id)
    if not matrix_room_id:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Circle chat room not provisioned yet",
        )

    if not settings.livekit_api_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice rooms are not configured on this server",
        )

    # Mint a LiveKit JWT scoped to this room + user
    display_name = user.get("first_name") or user["id"]
    token = (
        AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity(display_name)
        .with_name(display_name)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=matrix_room_id,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .with_ttl(timedelta(hours=4))
        .to_jwt()
    )

    return {
        "success": True,
        "data": {
            "token": token,
            "livekit_url": settings.livekit_url,
            "room_name": matrix_room_id,
        },
    }
