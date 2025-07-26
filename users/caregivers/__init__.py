from fastapi import APIRouter

from .caregiver_router import router as caregiver_router

router = APIRouter(prefix="/caregivers")

router.include_router(caregiver_router)

from .caregiver import Caregiver
from .caregiver_crud import caregiver_crud

__all__ = [
    "router",
    "Caregiver",
    "caregiver_crud",
]