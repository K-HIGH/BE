"""
안전 구역 라우터

안전 구역 관련 API 엔드포인트
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session

from common.postgres.database import get_session
from users.safety_areas.dto import SafetyAreaCreateReq, SafetyAreaGetRes, SafetyAreaUpdateReq
from users.safety_areas.safety_area_crud import safety_area_crud
from users.user import User
from users.user_router import get_current_user

router = APIRouter(tags=["Safety Areas API"])


@router.get(
    "/",
    response_model=List[SafetyAreaGetRes],
    responses={
        200: {
            "description": "Safety Areas fetched",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "safety_area_id": 1,
                            "safety_area_name": "Safety Area 1",
                            "loc_safety_area": "POINT(127.000000 37.000000)",
                            "dist_safety_radius": 1000.0
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
async def get_safety_areas(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """안전 구역 목록 조회"""
    safety_areas = safety_area_crud.get_by_user_id(db, user.user_id)
    return JSONResponse(
        status_code=200,
        content=[
            SafetyAreaGetRes(
                safety_area_id=safety_area.safety_area_id,
                safety_area_name=safety_area.safety_area_name,
                loc_safety_area=safety_area.loc_safety_area,
                dist_safety_radius=safety_area.dist_safety_radius
            ) for safety_area in safety_areas
        ]
    )


@router.post(
    "/",
    response_model=SafetyAreaGetRes,
    responses={
        200: {
            "description": "Safety Area created",
            "content": {
                "application/json": {
                    "example": {
                        "safety_area_id": 1,
                        "safety_area_name": "Safety Area 1",
                        "loc_safety_area": "POINT(127.000000 37.000000)",
                        "dist_safety_radius": 1000.0
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
async def create_safety_area(
    safety_area: SafetyAreaCreateReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """안전 구역 생성"""
    safety_area = safety_area_crud.create_safety_area(db, user.user_id, safety_area)
    return JSONResponse(
        status_code=200,
        content=SafetyAreaGetRes(
            safety_area_id=safety_area.safety_area_id,
            safety_area_name=safety_area.safety_area_name,
            loc_safety_area=safety_area.loc_safety_area,
            dist_safety_radius=safety_area.dist_safety_radius
        )
    )


@router.get(
    "/{safety_area_id}",
    response_model=SafetyAreaGetRes,
    responses={
        200: {
            "description": "Safety Area fetched",
            "content": {
                "application/json": {
                    "example": {
                        "safety_area_id": 1,
                        "safety_area_name": "Safety Area 1",
                        "loc_safety_area": "POINT(127.000000 37.000000)",
                        "dist_safety_radius": 1000.0
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "safety_area_id": 1,
                        "safety_area_name": "Safety Area 1",
                        "loc_safety_area": "POINT(127.000000 37.000000)",
                        "dist_safety_radius": 1000.0
                    }
                }
            }
        },
        404: {
            "description": "Safety Area not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Safety Area not found"}
                }
            }
        }
    }
)
async def get_safety_area(
    safety_area_id: int, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_session)
):
    """특정 안전 구역 조회"""
    safety_area = safety_area_crud.get_by_id(db, safety_area_id)
    if not safety_area or safety_area.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="Safety Area not found")
    
    return JSONResponse(
        status_code=200,
        content=SafetyAreaGetRes(
            safety_area_id=safety_area.safety_area_id,
            safety_area_name=safety_area.safety_area_name,
            loc_safety_area=safety_area.loc_safety_area,
            dist_safety_radius=safety_area.dist_safety_radius
        )
    )


@router.put(
    "/{safety_area_id}",
    response_model=SafetyAreaGetRes,
    responses={
        200: {
            "description": "Safety Area updated",
            "content": {
                "application/json": {
                    "example": {
                        "safety_area_id": 1,
                        "safety_area_name": "Safety Area 1",
                        "loc_safety_area": "POINT(127.000000 37.000000)",
                        "dist_safety_radius": 1000.0
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
            "description": "Safety Area not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Safety Area not found"}
                }
            }
        }
    }
)
async def update_safety_area(
    safety_area_id: int,
    safety_area: SafetyAreaUpdateReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """안전 구역 수정"""
    safety_area = safety_area_crud.get_by_id(db, safety_area_id)
    if not safety_area or safety_area.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="Safety Area not found")

    safety_area = safety_area_crud.update_safety_area(db, safety_area_id, safety_area)
    return JSONResponse(
        status_code=200,
        content=SafetyAreaGetRes(
            safety_area_id=safety_area.safety_area_id,
            safety_area_name=safety_area.safety_area_name,
            loc_safety_area=safety_area.loc_safety_area,
            dist_safety_radius=safety_area.dist_safety_radius
        )
    )

@router.delete(
    "/{safety_area_id}",
    responses={
        204: {
            "description": "Safety Area deleted",
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
            "description": "Safety Area not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Safety Area not found"}
                }
            }
        }
    }
)
async def delete_safety_area(
    safety_area_id: int, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_session)
):
    """안전 구역 삭제"""
    safety_area = safety_area_crud.get_by_id(db, safety_area_id)
    if not safety_area or safety_area.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="Safety Area not found")
    safety_area_crud.delete_safety_area(db, safety_area_id)
    return JSONResponse(
        status_code=200, 
        content={"detail": "Safety Area deleted"}
    )