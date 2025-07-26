from typing import List, Optional
from sqlmodel import select
from sqlalchemy.orm import Session

from common.postgres.crud.base import CRUDBase
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


safety_area_crud = CRUDSafetyArea(SafetyArea)