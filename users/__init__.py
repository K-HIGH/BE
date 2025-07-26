from fastapi import APIRouter

from .user_router import router as user_router
from .caregivers import router as caregiver_router
from .safety_area_router import router as safety_area_router

router = APIRouter(prefix="/users")

router.include_router(user_router)
router.include_router(caregiver_router)
router.include_router(safety_area_router)

from .user import User
from .caregiver import Caregiver
from .safety_area import SafetyArea


__all__ = [
    "router",
    "User",
    "Caregiver",
    "SafetyArea",
]