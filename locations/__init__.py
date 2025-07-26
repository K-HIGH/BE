from fastapi import APIRouter

from .favorite import router as favorite_router

router = APIRouter(prefix="/locations")

router.include_router(favorite_router)

from .favorite import LocationFavorite
from .route import RouteHistory

__all__ = [
    "router",
    "LocationFavorite",
    "RouteHistory",
]