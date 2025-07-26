from fastapi import APIRouter

from .favorite_router import router as favorite_router

router = APIRouter(prefix="/favorite")

router.include_router(favorite_router)


from .favorite import LocationFavorite

__all__ = [
    "router",
    "LocationFavorite",
]