from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session

from common.memcache.database import memcache_client
from auth import get_current_user
from common.postgres.database import get_session
from users.caregivers import caregiver_crud
from users import User
from users.user_crud import user_crud
from .track_dto import TrackGetRes, TrackUpdateReq


router = APIRouter(tags=["Track API"])


@router.get(
    "/{user_ulid}",
    responses={
        200: {
            "description": "Track",
            "content": {
                "application/json": {
                    "example": {
                        "latitude": 37.485095,
                        "longitude": 126.88456,
                        "altitude": 100.0,
                        "speed": 10.0,
                        "direction": 100.0
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
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "Forbidden"}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "User Not Found"}
                }
            }
        }
    }
)
async def get_track(
    user_ulid: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    if not (target_user := user_crud.get_by_ulid(db, user_ulid)):
        return JSONResponse(
            status_code=404, 
            content={
                "detail": "User Not Found"
            })
    
    caregivers = caregiver_crud.get_by_user_id(db, user.user_id)
    
    if not caregivers or target_user.user_id not in [caregiver.target_id for caregiver in caregivers]:
        return JSONResponse(
            status_code=403, 
            content={
                "detail": "Forbidden"
            })

    track = memcache_client.get(str(target_user.user_id))
    if not track:
        return JSONResponse(
            status_code=404, 
            content={
                "detail": "Track Not Found"
            })
    return TrackGetRes(**track)

@router.put(
    "/",
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {"detail": "OK"}
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
async def update_track(
    req: TrackUpdateReq,
    user: User = Depends(get_current_user)
):
    memcache_client.set(str(user.user_id), req.model_dump(), expire=5)
    return JSONResponse(
        status_code=200, 
        content={
            "detail": "OK"
        })
