"""
피보호자 라우터

피보호자 관련 API 엔드포인트
"""

from typing import List
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session

from users.caregivers.caregiver_crud import caregiver_crud, taker_crud
from users.caregivers.dto import CaregiverGetRes, TakerApproveReq
from users.user import User
from common.postgres.database import get_session
from auth import get_current_user

router = APIRouter(tags=["Taker API"])


@router.get(
    "/", 
    response_model=List[CaregiverGetRes],
    responses={
        200: {
            "description": "Takers",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "caregiver_id": 1,
                            "user_id": 1,
                            "target_id": 2,
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
async def get_takers(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """피보호자 목록 조회"""
    takers = taker_crud.get_by_target_id(db, user.user_id)
    return takers

@router.post(
    "/", 
    response_model=CaregiverGetRes,
    responses={
        200: {
            "description": "Taker created",
            "content": {
                "application/json": {
                    "example": {
                        "caregiver_id": 1,
                        "user_id": 1,
                        "target_id": 2,
                        "created_at": "2021-01-01T00:00:00",
                        "updated_at": "2021-01-01T00:00:00"
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
            "description": "Taker not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Taker not found"}
                }
            }
        },
        409: {
            "description": "Taker already approved or rejected",
            "content": {
                "application/json": {
                    "example": {"detail": "Taker already approved or rejected"}
                }
            }
        }
    }
)
async def create_taker(
    taker_req: TakerApproveReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """피보호자 생성"""
    if not (taker := taker_crud.get_by_caregiver_id(db, taker_req.caregiver_id)):
        raise HTTPException(status_code=404, detail="Taker not found")
    if taker.target_id != user.user_id:
        raise HTTPException(status_code=404, detail="Taker not found")
    if taker.is_approved is not None:
        raise HTTPException(status_code=409, detail="Taker already approved or rejected")
    
    taker = taker_crud.update_is_approved(db, taker.caregiver_id, taker_req.is_approved)
    return taker

@router.delete(
    "/{caregiver_id}", 
    response_model=CaregiverGetRes,
    responses={
        204: {
            "description": "Taker deleted",
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
            "description": "Taker not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Taker not found"}
                }
            }
        }
    }
)
async def delete_taker(
    caregiver_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """피보호자 삭제"""
    if not (taker := taker_crud.get_by_caregiver_id(db, caregiver_id)):
        raise HTTPException(status_code=404, detail="Taker not found")
    if taker.target_id != user.user_id:
        raise HTTPException(status_code=404, detail="Taker not found")
    
    taker_crud.delete_taker_relationship(db, caregiver_id)
    return Response(status_code=204)