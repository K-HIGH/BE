from fastapi import APIRouter

from .auth_router import router as auth_router

router = APIRouter(prefix="/auth")

router.include_router(auth_router)


from .auth_router import get_current_user

__all__ = [
    "router", 
    "get_current_user",
]