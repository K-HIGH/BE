"""
경로 기록 라우터

경로 탐색 기록 관련 API 엔드포인트
"""

import os
from typing import List
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session

from auth import get_current_user
from common.postgres.database import get_session
from common.tmap.api_client import TmapCoordinate, get_transit_directions
from locations.routes.dto import RouteHistoryRes, RouteReq
from locations.routes.route import RouteHistory
from locations.routes.route_crud import route_history_crud
from users.user import User

router = APIRouter(tags=["Route API"])


@router.get(
    "/",
    response_model=List[RouteHistoryRes],
    responses={
        200: {
            "description": "Route History",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "route_id": 1,
                            "user_id": 1,
                            "src": {"name": "출발지", "address": "서울시 종로구 종로동"},
                            "dst": {"name": "도착지", "address": "서울시 종로구 종로동"},
                            "routes": [
                                {
                                    "name": "경로 1",
                                    "distance": 1000,
                                    "duration": 10,
                                    "polyline": "M123.456,789.012 L456.789,123.456"
                                }
                            ],
                            "created_at": "2021-01-01T00:00:00"
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
async def get_route_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """경로 탐색 기록 목록 조회"""
    route_histories = route_history_crud.get_by_user_id(db, user.user_id)
    return JSONResponse(
        status_code=200,
        content=[
            RouteHistoryRes(
                route_id=route_history.route_id, 
                user_id=route_history.user_id, 
                src=route_history.src, 
                dst=route_history.dst, 
                routes=route_history.routes, 
                created_at=route_history.created_at
            ) for route_history in route_histories
        ]
    )


@router.get(
    "/{route_id}",
    response_model=RouteHistoryRes,
    responses={
        200: {
            "description": "Route History",
            "content": {
                "application/json": {
                    "example": {
                        "route_id": 1,
                        "user_id": 1,
                        "src": {"name": "출발지", "address": "서울시 종로구 종로동"},
                        "dst": {"name": "도착지", "address": "서울시 종로구 종로동"},
                        "routes": [
                            {
                                "name": "경로 1",
                                "distance": 1000,
                                "duration": 10,
                                "polyline": "M123.456,789.012 L456.789,123.456"
                            }
                        ],
                        "created_at": "2021-01-01T00:00:00"
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
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Route history not found"}
                }
            }
        }
    }
)
async def get_route_history_by_id(
    route_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """경로 탐색 기록 상세 조회"""
    route_history = route_history_crud.get_by_route_id(db, route_id)
    if route_history.user_id != user.user_id:
        raise HTTPException(status_code=404, detail=f"Route history with route_id {route_id} not found")
    
    return JSONResponse(
        status_code=200,
        content=RouteHistoryRes(
            route_id=route_history.route_id,
            user_id=route_history.user_id,
            src=route_history.src,
            dst=route_history.dst,
            routes=route_history.routes,
            created_at=route_history.created_at
        )
    )

@router.post(
    "/",
    response_model=RouteHistoryRes,
    responses={
        201: {
            "description": "Created",
            "content": {
                "application/json": {
                    "example": {
                        "route_id": 1,
                        "user_id": 1,
                        "src": {"name": "출발지", "address": "서울시 종로구 종로동"},
                        "dst": {"name": "도착지", "address": "서울시 종로구 종로동"},
                        "routes": [
                            {
                                "name": "경로 1",
                                "distance": 1000,
                                "duration": 10,
                                "polyline": "M123.456,789.012 L456.789,123.456"
                            }
                        ],
                        "created_at": "2021-01-01T00:00:00"
                    }
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Bad Request"}
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
    }
)
async def find_route(
    route_req: RouteReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """경로 탐색 기록 생성"""
    routes = await get_transit_directions(
        api_key=os.getenv("TMAP_API_KEY"),
        origin=route_req.src,
        destination=route_req.dst,
        count=route_req.count
    )
    
    route_history = RouteHistory(
        user_id=user.user_id,
        src=route_req.src,
        dst=route_req.dst,
        routes=routes
    )

    created_route_history = route_history_crud.create_route_history(db, route_history)

    return JSONResponse(
        status_code=201,
        content=[
            RouteHistoryRes(
                route_id=created_route_history.route_id,
                user_id=created_route_history.user_id,
                src=created_route_history.src,
                dst=created_route_history.dst,
                routes=created_route_history.routes,
                created_at=created_route_history.created_at
            )
        ]
    )


@router.delete(
    "/{route_id}",
    responses={
        204: {
            "description": "No Content"
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
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Route history not found"}
                }
            }
        }
    }
)
async def delete_route_history(
    route_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """경로 탐색 기록 삭제"""
    route_history = route_history_crud.get_by_route_id(db, route_id)
    if route_history.user_id != user.user_id:
        raise HTTPException(status_code=404, detail=f"Route history with route_id {route_id} not found")
    
    route_history_crud.delete_route_history(db, route_id)
    return Response(status_code=204)