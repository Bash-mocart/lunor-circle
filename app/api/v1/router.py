from fastapi import APIRouter

from app.api.v1.endpoints import circles, voice

router = APIRouter()
router.include_router(circles.router, prefix="/circles", tags=["circles"])
router.include_router(voice.router, tags=["voice"])
