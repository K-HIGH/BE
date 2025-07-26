from fastapi import APIRouter

from .route_router import router as route_router


router = APIRouter(prefix="/routes")

router.include_router(route_router)


from .route import RouteHistory
from .route_crud import route_history_crud


__all__ = [
    "RouteHistory",
    "route_history_crud",
]