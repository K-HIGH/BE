from fastapi import APIRouter

from .safety_area_router import router as safety_area_router

router = APIRouter(prefix="/safety-areas")

router.include_router(safety_area_router)


from .safety_area import SafetyArea
from .safety_area_crud import safety_area_crud

__all__ = [
    "router",
    "SafetyArea",
    "safety_area_crud",
]