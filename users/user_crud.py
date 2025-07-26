"""
사용자 CRUD 작업

사용자 정보, 프로필, 알림 설정에 대한 CRUD 작업
"""

from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from common.postgres.crud.base import CRUDBase
from .user import User, UserProfile, UserAlert
from .caregivers.caregiver import Caregiver
from .safety_area import SafetyArea
from common.postgres.crud.base import OAuthPlatform


class CRUDUser(CRUDBase[User, None, None]):
    """사용자 CRUD 작업"""
    
    def get_by_uuid(self, db: Session, user_uuid: str) -> Optional[User]:
        """UUID로 사용자 조회"""
        statement = select(User).where(User.user_uuid == user_uuid)
        return db.exec(statement).first()
    
    def get_by_oauth(self, db: Session, platform: OAuthPlatform, openid: str) -> Optional[User]:
        """OAuth 정보로 사용자 조회"""
        statement = select(User).where(
            User.oauth_platform == platform,
            User.openid == openid
        )
        return db.exec(statement).first()
    
    def get_with_profile(self, db: Session, user_id: int) -> Optional[User]:
        """프로필과 함께 사용자 조회"""
        statement = select(User).options(joinedload(User.profile)).where(User.user_id == user_id)
        return db.exec(statement).first()
    
    def get_with_alert(self, db: Session, user_id: int) -> Optional[User]:
        """알림 설정과 함께 사용자 조회"""
        statement = select(User).options(joinedload(User.alert)).where(User.user_id == user_id)
        return db.exec(statement).first()


class CRUDUserProfile(CRUDBase[UserProfile, None, None]):
    """사용자 프로필 CRUD 작업"""
    
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[UserProfile]:
        """사용자 ID로 프로필 조회"""
        statement = select(UserProfile).where(UserProfile.user_id == user_id)
        return db.exec(statement).first()
    
    def update_by_user_id(self, db: Session, user_id: int, user_name: str, phone: str, is_caregiver: bool = False) -> Optional[UserProfile]:
        """사용자 ID로 프로필 업데이트"""
        profile = self.get_by_user_id(db, user_id)
        if profile:
            profile.user_name = user_name
            profile.phone = phone
            profile.is_caregiver = is_caregiver
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile


class CRUDUserAlert(CRUDBase[UserAlert, None, None]):
    """사용자 알림 설정 CRUD 작업"""
    
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[UserAlert]:
        """사용자 ID로 알림 설정 조회"""
        statement = select(UserAlert).where(UserAlert.user_id == user_id)
        return db.exec(statement).first()
    
    def update_fcm_token(self, db: Session, user_id: int, fcm_token: str) -> Optional[UserAlert]:
        """FCM 토큰 업데이트"""
        alert = self.get_by_user_id(db, user_id)
        if alert:
            alert.fcm_token = fcm_token
            db.add(alert)
            db.commit()
            db.refresh(alert)
        return alert
    
    def toggle_alert(self, db: Session, user_id: int) -> Optional[UserAlert]:
        """알림 설정 토글"""
        alert = self.get_by_user_id(db, user_id)
        if alert:
            alert.is_alert = not alert.is_alert
            db.add(alert)
            db.commit()
            db.refresh(alert)
        return alert


class CRUDCaregiver(CRUDBase[Caregiver, None, None]):
    """보호자 CRUD 작업"""
    
    def get_by_user_id(self, db: Session, user_id: int) -> List[Caregiver]:
        """사용자 ID로 보호자 목록 조회"""
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
    
    def delete_caregiver_relationship(self, db: Session, user_id: int, target_id: int) -> bool:
        """보호자 관계 삭제"""
        statement = select(Caregiver).where(
            Caregiver.user_id == user_id,
            Caregiver.target_id == target_id
        )
        caregiver = db.exec(statement).first()
        if caregiver:
            db.delete(caregiver)
            db.commit()
            return True
        return False


# CRUD 인스턴스 생성
user_crud = CRUDUser(User)
user_profile_crud = CRUDUserProfile(UserProfile)
user_alert_crud = CRUDUserAlert(UserAlert)