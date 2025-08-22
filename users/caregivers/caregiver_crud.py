from typing import List
from sqlmodel import select
from sqlalchemy.orm import Session

from common.postgres.crud.base import CRUDBase
from users.user import User
from .caregiver import Caregiver
from .dto import CaregiverUpdateReq


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

    def update_caregiver_relationship(self, db: Session, caregiver_id: int, caregiver_update_req: CaregiverUpdateReq) -> Caregiver:
        """보호자 관계 업데이트"""
        statement = select(Caregiver).where(Caregiver.caregiver_id == caregiver_id)
        caregiver = db.exec(statement).first()
        if caregiver:
            if caregiver_update_req.relationship_type:
                caregiver.relationship_type = caregiver_update_req.relationship_type
            if caregiver_update_req.description:
                caregiver.description = caregiver_update_req.description
            db.commit()
            db.refresh(caregiver)
            return caregiver
        else:
            raise ValueError(f"Caregiver with caregiver_id {caregiver_id} not found")
    
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

class CRUDTaker(CRUDBase[Caregiver, None, None]):
    """피보호자 CRUD 작업"""
    
    def get_by_target_id(self, db: Session, target_id: int) -> Caregiver:
        """피보호자 ID로 피보호자 조회"""
        statement = select(Caregiver).where(Caregiver.target_id == target_id)
        return db.exec(statement).first()
    
    def update_is_approved(self, db: Session, caregiver_id: int, is_approved: bool) -> Caregiver:
        """피보호자 승인 여부 업데이트"""
        statement = select(Caregiver).where(Caregiver.caregiver_id == caregiver_id)
        caregiver = db.exec(statement).first()
        if caregiver:
            caregiver.is_approved = is_approved
            db.commit()
            db.refresh(caregiver)
            return caregiver
        else:
            raise ValueError(f"Caregiver with caregiver_id {caregiver_id} not found")
    
    def delete_taker_relationship(self, db: Session, caregiver_id: int) -> bool:
        """피보호자 관계 삭제"""
        statement = select(Caregiver).where(Caregiver.caregiver_id == caregiver_id)
        caregiver = db.exec(statement).first()
        if caregiver:
            db.delete(caregiver)
            db.commit()
            return True
        else:
            raise ValueError(f"Caregiver with caregiver_id {caregiver_id} not found")

caregiver_crud = CRUDCaregiver(Caregiver)
taker_crud = CRUDTaker(Caregiver)