"""
보호자 라우터

보호자 관련 API 엔드포인트
"""

from typing import List
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session

from users.user_crud import user_crud, user_profile_crud
from users.caregivers.caregiver_crud import caregiver_crud
from users.caregivers.dto import CaregiverGetRes, CaregiverGetResWithTarget
from users.user import User
from common.postgres.database import get_session
from auth import get_current_user
from users.user_dto import UserViewRes

router = APIRouter(tags=["Caregivers API"])


@router.get(
    "/",
    response_model=List[CaregiverGetRes],
    responses={
        200: {
            "description": "Caregivers",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "caregiver_id": 1,
                            "user_id": 1,
                            "target_id": 2,
                            "relationship_type": "caregiver",
                            "description": "description",
                            "created_at": "2021-01-01T00:00:00",
                            "updated_at": "2021-01-01T00:00:00"
                        }
                    ]
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
async def get_caregivers(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """보호자 목록 조회"""
    caregivers = caregiver_crud.get_by_user_id(db, user.user_id)
    return JSONResponse(
        status_code=200, 
        content=[
            CaregiverGetRes(
                caregiver_id=caregiver.caregiver_id,
                user_id=caregiver.user_id,
                target_id=caregiver.target_id,
                relationship_type=caregiver.relationship_type,
                description=caregiver.description,
                created_at=caregiver.created_at,
                updated_at=caregiver.updated_at
            ) for caregiver in caregivers
        ]
    )

@router.get(
    "/{caregiver_id}",
    response_model=CaregiverGetResWithTarget,
    responses={
        200: {
            "description": "Caregiver",
            "content": {
                "application/json": {
                    "example": {
                        "caregiver_id": 1,
                        "user_id": 1,
                        "target_id": 2,
                        "created_at": "2021-01-01T00:00:00",
                        "updated_at": "2021-01-01T00:00:00",
                        "target": {
                            "user_id": 2,
                            "user_name": "John Doe",
                            "phone": "010-1234-5678",
                            "is_caregiver": True,
                            "is_helper": True,
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
        },
        404: {
            "description": "Caregiver not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Caregiver not found"}
                }
            }
        }
    }
)
async def get_caregiver(
    caregiver_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """보호자 조회"""
    caregiver = caregiver_crud.get_by_caregiver_id(db, caregiver_id)
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    if caregiver.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    
    if not caregiver.is_approved:
        target = None
    else:
        target = user_crud.get_by_user_id(db, caregiver.target_id)
        target_profile = user_profile_crud.get_by_user_id(db, caregiver.target_id)

        target = UserViewRes(
            user_id=target.user_id,
            user_name=target_profile.user_name,
            email=target.email,
            phone=target_profile.phone,
            address=target_profile.address,
            emergency_contact=target_profile.emergency_contact,
        )
    
    return JSONResponse(
        status_code=200,
        content=CaregiverGetResWithTarget(
            caregiver_id=caregiver.caregiver_id,
            user_id=caregiver.user_id,
            target_id=caregiver.target_id,
            relationship_type=caregiver.relationship_type,
            description=caregiver.description,
            created_at=caregiver.created_at,
            updated_at=caregiver.updated_at,
            target=target
        )
    )

@router.post(
    "/",
    response_model=CaregiverGetRes,
    responses={
        200: {
            "description": "Caregiver created",
            "content": {
                "application/json": {
                    "example": {
                        "caregiver_id": 1,
                        "user_id": 1,
                        "target_id": 2,
                        "relationship_type": "caregiver",
                        "description": "description",
                        "created_at": "2021-01-01T00:00:00",
                        "updated_at": "2021-01-01T00:00:00",
                        "target": {
                            "user_id": 2,
                            "user_name": "John Doe",
                            "email": "test@test.com",
                            "phone": "010-1234-5678",
                            "address": "1234567890",
                            "emergency_contact": "1234567890"
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
        },
        404: {
            "description": "Target not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Target not found"}
                }
            }
        },
        409: {
            "description": "Caregiver already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "Caregiver already exists"}
                }
            }
        }
    }
)
async def create_caregiver(
    target_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """보호자 관계 생성"""
    target = caregiver_crud.get_by_target_id(db, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    if target.user_id == user.user_id:
        raise HTTPException(status_code=409, detail="Caregiver already exists")
    
    caregiver = caregiver_crud.create_caregiver_relationship(db, user.user_id, target_id)
    return JSONResponse(
        status_code=200,
        content=CaregiverGetRes(
            caregiver_id=caregiver.caregiver_id,
            user_id=caregiver.user_id,
            target_id=caregiver.target_id,
            relationship_type=caregiver.relationship_type,
            description=caregiver.description,
            created_at=caregiver.created_at,
            updated_at=caregiver.updated_at
        )
    )


@router.delete(
    "/{caregiver_id}",
    responses={
        204: {
            "description": "Caregiver deleted",
            "content": {
                "application/json": {
                    "example": None
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
        404: {
            "description": "Caregiver not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Caregiver not found"}
                }
            }
        }
    }
)
async def delete_caregiver(
    caregiver_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """보호자 관계 삭제"""
    caregiver = caregiver_crud.get_by_caregiver_id(db, caregiver_id)
    if not caregiver or caregiver.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="Caregiver not found")

    caregiver_crud.delete_caregiver_relationship(db, caregiver_id)
    return Response(status_code=204)