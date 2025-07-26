from datetime import datetime
from typing import List, Optional
from sqlmodel import func, select
from sqlalchemy.orm import Session

from common.postgres.crud.base import CRUDBase
from users.safety_areas.dto import SafetyAreaCreateReq, SafetyAreaUpdateReq
from .safety_area import SafetyArea


class CRUDSafetyArea(CRUDBase[SafetyArea, None, None]):
    """안전 구역 CRUD 작업"""
    
    def get_by_user_id(self, db: Session, user_id: int) -> List[SafetyArea]:
        """사용자 ID로 안전 구역 목록 조회"""
        statement = select(SafetyArea).where(SafetyArea.user_id == user_id)
        return db.exec(statement).all()
    
    def get_by_id(self, db: Session, safety_area_id: int) -> Optional[SafetyArea]:
        """안전 구역 ID로 조회"""
        statement = select(SafetyArea).where(SafetyArea.safety_area_id == safety_area_id)
        return db.exec(statement).first()

    def create_safety_area(self, db: Session, user_id: int, safety_area: SafetyAreaCreateReq) -> SafetyArea:
        """안전 구역 생성"""
        safety_area = SafetyArea(
            user_id=user_id,
            safety_area_name=safety_area.safety_area_name,
            loc_safety_area=func.ST_SetSRID(func.ST_MakePoint(safety_area.loc_safety_area[0], safety_area.loc_safety_area[1]), 4326),
            dist_safety_radius=safety_area.dist_safety_radius
        )
        db.add(safety_area)
        db.commit()
        db.refresh(safety_area)
        return safety_area
    
    def check_safety_area_violation(self, db: Session, user_id: int, current_location: tuple[float, float]) -> Optional[int]:
        """안전 구역 위반 여부 확인"""
        user_coor = func.ST_SetSRID(func.ST_MakePoint(current_location[0], current_location[1]), 4326)

        stmt = select(SafetyArea).where(
            SafetyArea.user_id == user_id,
            func.ST_DWithin(
                SafetyArea.loc_safety_area,
                user_coor,
                SafetyArea.dist_safety_radius
            )
        )
        inside = db.exec(stmt).first()
        if inside:
            return inside.safety_area_id
        else:
            return None

    def update_safety_area(self, db: Session, safety_area_id: int, safety_area: SafetyAreaUpdateReq) -> SafetyArea:
        """안전 구역 수정"""
        safety_area = self.get_by_id(db, safety_area_id)
        if not safety_area:
            raise ValueError(f"Safety area with id {safety_area_id} not found")

        if safety_area.safety_area_name is not None:
            safety_area.safety_area_name = safety_area.safety_area_name
        if safety_area.loc_safety_area is not None:
            safety_area.loc_safety_area = func.ST_SetSRID(func.ST_MakePoint(safety_area.loc_safety_area[0], safety_area.loc_safety_area[1]), 4326)
        if safety_area.dist_safety_radius is not None:
            safety_area.dist_safety_radius = safety_area.dist_safety_radius
        safety_area.updated_at = datetime.now()
        db.commit()
        db.refresh(safety_area)
        return safety_area

    def delete_safety_area(self, db: Session, safety_area_id: int) -> bool:
        """안전 구역 삭제"""
        safety_area = self.get_by_id(db, safety_area_id)
        if not safety_area:
            raise ValueError(f"Safety area with id {safety_area_id} not found")
        
        db.delete(safety_area)
        db.commit()
        return True

safety_area_crud = CRUDSafetyArea(SafetyArea)