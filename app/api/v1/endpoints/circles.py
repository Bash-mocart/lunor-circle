from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def list_circles(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    # TODO: implement
    return {"circles": []}
