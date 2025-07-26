from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session

from auth import get_current_user
from common.postgres.database import get_session
from locations.favorite.dto import LocationFavoriteCreateReq, LocationFavoriteRes, LocationFavoriteUpdateReq
from locations.favorite.favorite_crud import location_favorite_crud
from users.user import User

router = APIRouter(tags=["Location Favorite API"])


@router.get(
    "/",
    response_model=List[LocationFavoriteRes],
    responses={
        200: {
            "description": "LocationFavorite",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "location_id": 1,
                            "loc_name": "Location 1",
                            "loc_coor": "123,456",
                            "loc_desc": "Location 1 description",
                            "loc_info": {"key": "value"}
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
async def get_location_favorite(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    location_favorites = location_favorite_crud.get_by_user_id(db, user.user_id)
    return JSONResponse(
        status_code=200,
        content=[LocationFavoriteRes(
            location_id=location_favorite.location_id,
            loc_name=location_favorite.loc_name,
            loc_coor=location_favorite.loc_coor,
            loc_desc=location_favorite.loc_desc,
            loc_info=location_favorite.loc_info
        ) for location_favorite in location_favorites]
    )


@router.post(
    "/",
    response_model=LocationFavoriteRes,
    responses={
        200: {
            "description": "LocationFavorite created",
            "content": {
                "application/json": {
                    "example": {
                        "location_id": 1,
                        "loc_name": "Location 1",
                        "loc_coor": "123,456",
                        "loc_desc": "Location 1 description",
                        "loc_info": {"key": "value"}
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
async def create_location_favorite(
    location_favorite: LocationFavoriteCreateReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    location_favorite = location_favorite_crud.create_location_favorite(db, user.user_id, location_favorite)
    return JSONResponse(
        status_code=200,
        content=LocationFavoriteRes(
            location_id=location_favorite.location_id,
            loc_name=location_favorite.loc_name,
            loc_coor=location_favorite.loc_coor,
            loc_desc=location_favorite.loc_desc,
            loc_info=location_favorite.loc_info
        )
    )


@router.put(
    "/{location_id}",
    response_model=LocationFavoriteRes,
    responses={
        200: {
            "description": "LocationFavorite updated",
            "content": {
                "application/json": {
                    "example": {
                        "location_id": 1,
                        "loc_name": "Location 1",
                        "loc_coor": "123,456",
                        "loc_desc": "Location 1 description",
                        "loc_info": {"key": "value"}
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
            "description": "LocationFavorite not found",
            "content": {
                "application/json": {
                    "example": {"detail": "LocationFavorite not found"}
                }
            }
        }
    }
)
async def update_location_favorite(
    location_id: int,
    location_favorite: LocationFavoriteUpdateReq,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    location_favorite_db = location_favorite_crud.get_by_location_id(db, location_id)
    if location_favorite_db is None or location_favorite_db.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="LocationFavorite not found")

    location_favorite = location_favorite_crud.update_location_favorite(db, location_id, location_favorite)
    return JSONResponse(
        status_code=200,
        content=LocationFavoriteRes(
            location_id=location_favorite.location_id,
            loc_name=location_favorite.loc_name,
            loc_coor=location_favorite.loc_coor,
            loc_desc=location_favorite.loc_desc,
            loc_info=location_favorite.loc_info
        )
    )


@router.delete(
    "/{location_id}",
    responses={
        204: {
            "description": "LocationFavorite deleted",
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
            "description": "LocationFavorite not found",
            "content": {
                "application/json": {
                    "example": {"detail": "LocationFavorite not found"}
                }
            }
        }
    }
)
async def delete_location_favorite(
    location_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    location_favorite_db = location_favorite_crud.get_by_location_id(db, location_id)
    if location_favorite_db is None or location_favorite_db.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="LocationFavorite not found")

    location_favorite_crud.delete_location_favorite(db, location_id)
    return Response(status_code=204)
