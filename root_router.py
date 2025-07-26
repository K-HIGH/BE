from fastapi import APIRouter

from users import router as users_router
from auth import router as auth_router
from locations import router as locations_router


root_router = APIRouter(prefix="/api/v1")

root_router.include_router(users_router)
root_router.include_router(auth_router)

root_router.include_router(locations_router)
