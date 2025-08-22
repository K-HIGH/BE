from fastapi import APIRouter

from .caregiver_router import router as caregiver_inner_router
from .caretaker_router import router as taker_inner_router


caregiver_router = APIRouter(prefix="/caregivers")
taker_router = APIRouter(prefix="/takers")

caregiver_router.include_router(caregiver_inner_router)
taker_router.include_router(taker_inner_router)

from .caregiver import Caregiver
from .caregiver_crud import caregiver_crud, taker_crud

__all__ = [
    "caregiver_router",
    "taker_router",
    "Caregiver",
    "caregiver_crud",
    "taker_crud",
]