from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session

from auth import get_current_user
from common.memcache.database import memcache_client
from common.postgres.database import get_session
from users.user_dto import UserAlertRes, UserProfileUpdateReq, UserProfileRes, UserRes
from users.user_crud import user_alert_crud, user_crud, user_profile_crud

from .user import User


router = APIRouter(tags=["User API"])


@router.get(
    "/me",
    response_model=UserRes,
    responses={
        200: {
            "description": "User profile and alert fetched",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "user_id": 1,
                            "user_ulid": "1234567890",
                            "email": "test@test.com",
                            "oauth_platform": "google",
                            "openid": "1234567890",
                            "oauth_token": "1234567890",
                            "is_registered": True
                        },
                        "user_profile": {
                            "user_name": "John Doe",
                            "phone": "1234567890",
                            "address": "1234567890",
                            "emergency_contact": "1234567890",
                            "is_caregiver": True,
                            "is_helper": False
                        },
                        "user_alert": {
                            "fcm_token": "fcm_token",
                            "is_alert": True
                        }
                    }
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
    user_profile = user_profile_crud.get_by_user_id(db, user.user_id)
    user_alert = user_alert_crud.get_by_user_id(db, user.user_id)
    return JSONResponse(
        status_code=200, 
        content=UserRes(
            user=user,
            user_profile=UserProfileRes(
                user_name=user_profile.user_name,
                phone=user_profile.phone,
                address=user_profile.address,
                emergency_contact=user_profile.emergency_contact,
                is_caregiver=user_profile.is_caregiver,
                is_helper=user_profile.is_helper
            ),
            user_alert=UserAlertRes(
                fcm_token=user_alert.fcm_token,
                is_alert=user_alert.is_alert
            )
        ).model_dump(mode="json")
    )


@router.put(
    "/me/profile",
    response_model=UserRes,
    responses={
        200: {
            "description": "User profile updated",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "user_id": 1,
                            "user_ulid": "1234567890",
                            "email": "test@test.com",
                            "oauth_platform": "google",
                            "openid": "1234567890",
                            "oauth_token": "1234567890",
                            "is_registered": True
                        },
                        "user_profile": {
                            "user_name": "John Doe",
                            "phone": "1234567890",
                            "address": "1234567890",
                            "emergency_contact": "1234567890",
                            "is_caregiver": True,
                            "is_helper": False
                        },
                        "user_alert": {
                            "fcm_token": "fcm_token",
                            "is_alert": True
                        }
                    }
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
    user_alert = user_alert_crud.get_by_user_id(db, user.user_id)
    user_crud.update_registered_flag(db, user.user_id, True)
    user_alert = user_alert_crud.get_by_user_id(db, user.user_id)
    return JSONResponse(
        status_code=200, 
            content=UserRes(
            user=user,
            user_profile=UserProfileRes(
                user_name=user_profile.user_name,
                phone=user_profile.phone,
                address=user_profile.address,
                emergency_contact=user_profile.emergency_contact,
                is_caregiver=user_profile.is_caregiver,
                is_helper=user_profile.is_helper
            ),
            user_alert=UserAlertRes(
                fcm_token=user_alert.fcm_token,
                is_alert=user_alert.is_alert
            )
        ).model_dump(mode="json")
    )


@router.put(
    "/me/alert/fcm-token",
    response_model=UserRes,
    responses={
        200: {
            "description": "User alert fcm token updated",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "user_id": 1,
                            "user_ulid": "1234567890",
                            "email": "test@test.com",
                            "oauth_platform": "google",
                            "openid": "1234567890",
                            "oauth_token": "1234567890",
                            "is_registered": True
                        },
                        "user_profile": {
                            "user_name": "John Doe",
                            "phone": "1234567890",
                            "is_caregiver": True,
                            "is_helper": False
                        },
                        "user_alert": {
                            "fcm_token": "fcm_token",
                            "is_alert": True
                        }
                    }
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
    user_profile = user_profile_crud.get_by_user_id(db, user.user_id)
    return JSONResponse(
        status_code=200, 
        content=UserRes(
            user=user,
            user_profile=UserProfileRes(
                user_name=user_profile.user_name,
                phone=user_profile.phone,
                address=user_profile.address,
                emergency_contact=user_profile.emergency_contact,
                is_caregiver=user_profile.is_caregiver,
                is_helper=user_profile.is_helper
            ),
            user_alert=UserAlertRes(
                fcm_token=user_alert.fcm_token,
                is_alert=user_alert.is_alert
            )
        ).model_dump(mode="json")
    )


@router.put(
    "/me/alert/flag",
    response_model=UserRes,
    responses={
        200: {
            "description": "User alert flag updated",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "user_id": 1,
                            "user_ulid": "1234567890",
                            "email": "test@test.com",
                            "oauth_platform": "google",
                            "openid": "1234567890",
                            "oauth_token": "1234567890",
                            "is_registered": True
                        },
                        "user_profile": {
                            "user_name": "John Doe",
                            "phone": "1234567890",
                            "is_caregiver": True,
                            "is_helper": False
                        },
                        "user_alert": {
                            "fcm_token": "fcm_token",
                            "is_alert": True
                        }
                    }
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
    user_profile = user_profile_crud.get_by_user_id(db, user.user_id)
    return JSONResponse(
        status_code=200, 
        content=UserRes(
            user=user,
            user_profile=UserProfileRes(
                user_name=user_profile.user_name,
                phone=user_profile.phone,
                address=user_profile.address,
                emergency_contact=user_profile.emergency_contact,
                is_caregiver=user_profile.is_caregiver,
                is_helper=user_profile.is_helper
            ),
            user_alert=UserAlertRes(
                fcm_token=user_alert.fcm_token,
                is_alert=user_alert.is_alert
            )
        ).model_dump(mode="json")
    )


@router.delete(
    "/me",
    responses={
        204: {
            "description": "User deleted",
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
    memcache_client.delete(f"oauth:{user.oauth_platform}:{user.openid}")
    memcache_client.delete("track:" + str(user.user_id))
    return Response(status_code=204)

