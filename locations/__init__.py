from fastapi import APIRouter

from .favorite import router as favorite_router
from .routes import router as route_router

router = APIRouter(prefix="/locations")

router.include_router(favorite_router)
router.include_router(route_router)

from .favorite import LocationFavorite

__all__ = [
    "router",
    "LocationFavorite",
]