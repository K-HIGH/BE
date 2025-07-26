from typing import List
from sqlmodel import select
from sqlalchemy.orm import Session

from common.postgres.crud.base import CRUDBase
from .caregiver import Caregiver


class CRUDCaregiver(CRUDBase[Caregiver, None, None]):
    """보호자 CRUD 작업"""
    
    def get_by_user_id(self, db: Session, user_id: int) -> List[Caregiver]:
        """사용자 ID로 보호자 목록 조회"""
        statement = select(Caregiver).where(Caregiver.user_id == user_id)
        return db.exec(statement).all()


caregiver_crud = CRUDCaregiver(Caregiver)