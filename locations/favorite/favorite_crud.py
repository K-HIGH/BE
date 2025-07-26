

from typing import List

from sqlmodel import Session, select
from common.postgres.crud.base import CRUDBase
from locations.favorite.dto import LocationFavoriteCreateReq, LocationFavoriteUpdateReq
from locations.favorite.favorite import LocationFavorite


class CRUDLocationFavorite(CRUDBase[LocationFavorite, None, None]):
    """즐겨찾기 위치 정보 CRUD"""
    def get_by_user_id(self, db: Session, user_id: int) -> List[LocationFavorite]:
        """사용자 ID로 즐겨찾기 위치 정보 조회"""
        statement = select(LocationFavorite).where(LocationFavorite.user_id == user_id)
        return db.exec(statement).all()

    def get_by_location_id(self, db: Session, location_id: int) -> LocationFavorite:
        """즐겨찾기 위치 정보 조회"""
        statement = select(LocationFavorite).where(LocationFavorite.location_id == location_id)
        return db.exec(statement).first()

    def create_location_favorite(self, db: Session, user_id: int, location_favorite: LocationFavoriteCreateReq) -> LocationFavorite:
        """즐겨찾기 위치 정보 생성"""
        location_favorite = LocationFavorite(
            user_id=user_id,
            loc_name=location_favorite.loc_name,
            loc_coor=location_favorite.loc_coor,
            loc_desc=location_favorite.loc_desc,
            loc_info=location_favorite.loc_info
        )
        db.add(location_favorite)
        db.commit()
        db.refresh(location_favorite)
        return location_favorite
    
    def update_location_favorite(self, db: Session, location_id: int, location_favorite: LocationFavoriteUpdateReq) -> LocationFavorite:
        """즐겨찾기 위치 정보 수정"""
        statement = select(LocationFavorite).where(LocationFavorite.location_id == location_id)
        location_favorite = db.exec(statement).first()
        if location_favorite:
            if location_favorite.loc_name is not None:
                location_favorite.loc_name = location_favorite.loc_name
            if location_favorite.loc_coor is not None:
                location_favorite.loc_coor = location_favorite.loc_coor
            if location_favorite.loc_desc is not None:
                location_favorite.loc_desc = location_favorite.loc_desc
            if location_favorite.loc_info is not None:
                location_favorite.loc_info = location_favorite.loc_info
            db.commit()
            db.refresh(location_favorite)
            return location_favorite
        else:
            raise ValueError(f"LocationFavorite with location_id {location_id} not found")

    def delete_location_favorite(self, db: Session, location_id: int) -> bool:
        """즐겨찾기 위치 정보 삭제"""
        statement = select(LocationFavorite).where(LocationFavorite.location_id == location_id)
        location_favorite = db.exec(statement).first()
        if location_favorite:
            db.delete(location_favorite)
            db.commit()
            return True
        else:
            raise ValueError(f"LocationFavorite with location_id {location_id} not found")

location_favorite_crud = CRUDLocationFavorite(LocationFavorite)