

from fastapi import APIRouter

from .track_router import router as track_router


router = APIRouter(prefix="/track")

router.include_router(track_router)


__all__ = [
    "router",
]