from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session

from auth import get_current_user
from common.memcache.database import memcache_client
from common.postgres.database import get_session
from users.user_dto import UserAlertUpdateRes, UserProfileAlertRes, UserProfileUpdateReq, UserProfileUpdateRes
from users.user_crud import user_alert_crud, user_crud, user_profile_crud

from .user import User


router = APIRouter(tags=["User API"])


@router.get(
    "/me",
    response_model=UserProfileAlertRes,
    responses={
        200: {
            "description": "User profile and alert fetched",
            "content": {
                "application/json": {
                    "example": {
                        "user_name": "John Doe", 
                        "phone": "1234567890", 
                        "is_caregiver": True, 
                        "is_helper": False,
                        "fcm_token": "fcm_token", 
                        "is_alert": True}
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Unauthorized"}
                }
            }
        }
    }
)
async def get_user(
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_session)
):
    user_profile, user_alert = user_crud.get_with_profile_and_alert(db, user.user_id)
    return JSONResponse(
        status_code=200, 
        content=UserProfileAlertRes(
            user_name=user_profile.user_name, 
            phone=user_profile.phone, 
            is_caregiver=user_profile.is_caregiver, 
            is_helper=user_profile.is_helper,
            fcm_token=user_alert.fcm_token, 
            is_alert=user_alert.is_alert
        )
    )


@router.put(
    "/me/profile",
    response_model=UserProfileUpdateRes,
    responses={
        200: {
            "description": "User profile updated",
            "content": {
                "application/json": {
                    "example": {"user_name": "John Doe", "phone": "1234567890", "is_caregiver": True, "is_helper": False}
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Unauthorized"}
                }
            }
        }
    }
)
async def update_user_profile(
    user_profile: UserProfileUpdateReq, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_session)
):
    user_profile = user_profile_crud.update_by_user_id(db, user.user_id, user_profile)
    return JSONResponse(
        status_code=200, 
        content=UserProfileUpdateRes(
            user_name=user_profile.user_name, 
            phone=user_profile.phone, 
            is_caregiver=user_profile.is_caregiver, 
            is_helper=user_profile.is_helper
        )
    )


@router.put(
    "/me/alert/fcm-token",
    response_model=UserAlertUpdateRes,
    responses={
        200: {
            "description": "User alert fcm token updated",
            "content": {
                "application/json": {
                    "example": {"fcm_token": "fcm_token", "is_alert": True}
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Unauthorized"}
                }
            }
        }
    }
)
async def update_user_alert_fcm_token(
    fcm_token: str,
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_session)
):
    user_alert = user_alert_crud.update_fcm_token(db, user.user_id, fcm_token)
    return JSONResponse(
        status_code=200, 
        content=UserAlertUpdateRes(
            fcm_token=user_alert.fcm_token, 
            is_alert=user_alert.is_alert
        )
    )


@router.put(
    "/me/alert/flag",
    response_model=UserAlertUpdateRes,
    responses={
        200: {
            "description": "User alert flag updated",
            "content": {
                "application/json": {
                    "example": {"fcm_token": "fcm_token", "is_alert": True}
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Unauthorized"}
                }
            }
        }
    }
)
async def update_user_alert(
    is_alert: bool,
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_session)
):
    user_alert = user_alert_crud.update_alert_flag(db, user.user_id, is_alert)
    return JSONResponse(
        status_code=200, 
        content=UserAlertUpdateRes(
            fcm_token=user_alert.fcm_token, 
            is_alert=user_alert.is_alert
        )
    )


@router.delete(
    "/me",
    responses={
        200: {
            "description": "User deleted",
            "content": {
                "application/json": {
                    "example": {"message": "User deleted"}
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Unauthorized"}
                }
            }
        }
    }
)
async def delete_user(user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    user_crud.delete_user(db, user.user_id)
    memcache_client.delete("authorized_user:" + str(user.user_id))
    memcache_client.delete("track:" + str(user.user_id))
    return JSONResponse(
        status_code=200, 
        content={"message": "User deleted"}
    )

