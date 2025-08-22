"""
사용자 CRUD 작업

사용자 정보, 프로필, 알림 설정에 대한 CRUD 작업
"""

from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from common.postgres.crud.base import CRUDBase
from users.user_dto import UserProfileUpdateReq
from .user import User, UserProfile, UserAlert
from common.postgres.models import OAuthPlatform


class CRUDUser(CRUDBase[User, None, None]):
    """사용자 CRUD 작업"""
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[User]:
        """사용자 ID로 사용자 조회"""
        statement = select(User).where(User.user_id == user_id)
        return db.exec(statement).first()

    def get_by_user_ids(self, db: Session, user_ids: List[int]) -> List[User]:
        """사용자 ID 목록으로 사용자 조회"""
        statement = select(User).where(User.user_id.in_(user_ids))
        return db.exec(statement).all()

    def get_by_ulid(self, db: Session, user_ulid: str) -> Optional[User]:
        """UUID로 사용자 조회"""
        statement = select(User).where(User.user_ulid == user_ulid)
        return db.exec(statement).first()
    
    def get_by_oauth(self, db: Session, platform: OAuthPlatform, openid: str) -> Optional[User]:
        """OAuth 정보로 사용자 조회"""
        statement = select(User).where(
            User.oauth_platform == platform,
            User.openid == openid
        )
        return db.exec(statement).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        statement = select(User).where(User.email == email)
        return db.exec(statement).first()

    def get_with_profile(self, db: Session, user_id: int) -> Optional[User]:
        """프로필과 함께 사용자 조회"""
        statement = select(User).options(joinedload(User.profile)).where(User.user_id == user_id)
        return db.exec(statement).first()
    
    def get_with_alert(self, db: Session, user_id: int) -> Optional[User]:
        """알림 설정과 함께 사용자 조회"""
        statement = select(User).options(joinedload(User.alert)).where(User.user_id == user_id)
        return db.exec(statement).first()
    
    def get_with_profile_and_alert(self, db: Session, user_id: int) -> Optional[User]:
        """모든 정보와 함께 사용자 조회"""
        statement = select(User.profile, User.alert).where(User.user_id == user_id)
        return db.exec(statement).first()
    
    def create_user(self, db: Session, user: User) -> User:
        """사용자 생성"""        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_registered_flag(self, db: Session, user_id: int, is_registered: bool) -> Optional[User]:
        """유저 등록 여부 업데이트"""
        user = self.get_by_user_id(db, user_id)
        if user:
            user.is_registered = is_registered
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        else:
            raise ValueError(f"User with user_id {user_id} not found")

    def delete_user(self, db: Session, user_id: int) -> bool:
        """사용자 삭제"""
        user = self.get_by_user_id(db, user_id)
        if user:
            user_profile = user_profile_crud.get_by_user_id(db, user_id)
            user_alert = user_alert_crud.get_by_user_id(db, user_id)
            if user_profile:
                db.delete(user_profile)
            if user_alert:
                db.delete(user_alert)
            db.delete(user)
            db.commit()
            return True
        else:
            return False


class CRUDUserProfile(CRUDBase[UserProfile, None, None]):
    """사용자 프로필 CRUD 작업"""
    
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[UserProfile]:
        """사용자 ID로 프로필 조회"""
        statement = select(UserProfile).where(UserProfile.user_id == user_id)
        return db.exec(statement).first()
    
    def create_user_profile(self, db: Session, user_profile: UserProfile) -> Optional[UserProfile]:
        """사용자 프로필 생성"""
        user_profile = UserProfile(
            user_id=user_profile.user_id, 
            user_name=user_profile.user_name, 
            phone=user_profile.phone, 
            is_caregiver=user_profile.is_caregiver,
            is_helper=user_profile.is_helper
        )
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)
        return user_profile

    def update_by_user_id(self, db: Session, user_id: int, user_profile: UserProfileUpdateReq) -> Optional[UserProfile]:
        """사용자 ID로 프로필 업데이트"""
        profile = self.get_by_user_id(db, user_id)
        if profile:
            if user_profile.user_name:
                profile.user_name = user_profile.user_name
            if user_profile.phone:
                profile.phone = user_profile.phone
            if user_profile.is_caregiver is not None:
                profile.is_caregiver = user_profile.is_caregiver
            if user_profile.is_helper is not None:
                profile.is_helper = user_profile.is_helper
            db.add(profile)
            db.commit()
            db.refresh(profile)
            return profile
        else:
            raise ValueError(f"UserProfile with user_id {user_id} not found")


class CRUDUserAlert(CRUDBase[UserAlert, None, None]):
    """사용자 알림 설정 CRUD 작업"""
    
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[UserAlert]:
        """사용자 ID로 알림 설정 조회"""
        statement = select(UserAlert).where(UserAlert.user_id == user_id)
        return db.exec(statement).first()
    
    def create_user_alert(self, db: Session, user_alert: UserAlert) -> Optional[UserAlert]:
        """사용자 알림 설정 생성"""
        user_alert = UserAlert(user_id=user_alert.user_id, is_alert=user_alert.is_alert)
        db.add(user_alert)
        db.commit()
        db.refresh(user_alert)
        return user_alert

    def update_fcm_token(self, db: Session, user_id: int, fcm_token: str) -> Optional[UserAlert]:
        """FCM 토큰 업데이트"""
        alert = self.get_by_user_id(db, user_id)
        if alert:
            alert.fcm_token = fcm_token
            db.add(alert)
            db.commit()
            db.refresh(alert)
            return alert
        else:
            raise ValueError(f"UserAlert with user_id {user_id} not found")
    
    def update_alert_flag(self, db: Session, user_id: int, is_alert: bool) -> Optional[UserAlert]:
        """알림 설정 토글"""
        alert = self.get_by_user_id(db, user_id)
        if alert:
            alert.is_alert = is_alert
            db.add(alert)
            db.commit()
            db.refresh(alert)
            return alert
        else:
            raise ValueError(f"UserAlert with user_id {user_id} not found")

# CRUD 인스턴스 생성
user_crud = CRUDUser(User)
user_profile_crud = CRUDUserProfile(UserProfile)
user_alert_crud = CRUDUserAlert(UserAlert)