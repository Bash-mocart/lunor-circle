from fastapi import APIRouter

from app.api.v1.endpoints import circles

router = APIRouter()
router.include_router(circles.router, prefix="/circles", tags=["circles"])
