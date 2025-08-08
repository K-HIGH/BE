from typing import List
from sqlmodel import select
from sqlalchemy.orm import Session

from common.postgres.crud.base import CRUDBase
from .caregiver import Caregiver


class CRUDCaregiver(CRUDBase[Caregiver, None, None]):
    """보호자 CRUD 작업"""
    
    def get_by_caregiver_id(self, db: Session, caregiver_id: int) -> Caregiver:
        """보호자 ID로 보호자 조회"""
        statement = select(Caregiver).where(Caregiver.caregiver_id == caregiver_id)
        return db.exec(statement).first()
    
    def get_by_user_id(self, db: Session, user_id: int) -> List[Caregiver]:
        """사용자 ID로 보호대상 목록 조회"""
        statement = select(Caregiver).where(Caregiver.user_id == user_id)
        return db.exec(statement).all()
    
    def get_by_target_id(self, db: Session, target_id: int) -> List[Caregiver]:
        """대상 ID로 보호자 목록 조회"""
        statement = select(Caregiver).where(Caregiver.target_id == target_id)
        return db.exec(statement).all()
    
    def create_caregiver_relationship(self, db: Session, user_id: int, target_id: int) -> Caregiver:
        """보호자 관계 생성"""
        caregiver = Caregiver(user_id=user_id, target_id=target_id)
        db.add(caregiver)
        db.commit()
        db.refresh(caregiver)
        return caregiver
    
    def delete_caregiver_relationship(self, db: Session, caregiver_id: int) -> bool:
        """보호자 관계 삭제"""
        statement = select(Caregiver).where(
            Caregiver.caregiver_id == caregiver_id
        )
        caregiver = db.exec(statement).first()
        if caregiver:
            db.delete(caregiver)
            db.commit()
            return True
        else:
            raise ValueError(f"Caregiver with caregiver_id {caregiver_id} not found")

caregiver_crud = CRUDCaregiver(Caregiver)