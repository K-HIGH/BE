"""
사용자 관련 모델

사용자 정보, 프로필, 알림 설정을 관리하는 모델
"""

from ulid import ulid
from typing import Optional
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM

from sqlmodel import Field, Relationship, String

from common.postgres.models.base import TimestampMixin, OAuthPlatform


class User(TimestampMixin, table=True):
    """사용자 기본 정보"""
    __tablename__ = "users"
    
    user_id: Optional[int] = Field(default=None, primary_key=True, description="유저 구분 ID, jwt 토큰 부여 시 사용")
    user_ulid: str = Field(
        default_factory=lambda: str(ulid()), 
        sa_column=Column(String(26), unique=True, index=True),
        description="유저 UUID, 유저 구분 시 사용"
    )
    
    # OAuth 정보
    oauth_platform: Optional[OAuthPlatform] = Field(
        default=None, 
        sa_column=Column(ENUM(OAuthPlatform)),
        description="OAuth 플랫폼"
    )
    openid: Optional[str] = Field(default=None, max_length=64, description="OAuth openid")
    oauth_token: Optional[str] = Field(default=None, max_length=256, description="OAuth 토큰")
    email: str = Field(default=None, max_length=64, description="이메일")
    is_registered: bool = Field(default=False, description="유저 등록 여부, default: False")

    # 관계
    profile: Optional["UserProfile"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False}, cascade_delete=True)
    alert: Optional["UserAlert"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False}, cascade_delete=True)
    favorites: list["LocationFavorite"] = Relationship(back_populates="user", cascade_delete=True)
    route_histories: list["RouteHistory"] = Relationship(back_populates="user", cascade_delete=True)
    caregivers: list["Caregiver"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[Caregiver.user_id]"}
    )
    target_caregivers: list["Caregiver"] = Relationship(
        back_populates="target_user",
        sa_relationship_kwargs={"foreign_keys": "[Caregiver.target_id]"}
    )
    safety_areas: list["SafetyArea"] = Relationship(back_populates="user", cascade_delete=True)


class UserProfile(TimestampMixin, table=True):
    """사용자 프로필 정보"""
    __tablename__ = "users_profile"
    
    user_id: int = Field(primary_key=True, foreign_key="users.user_id", description="유저 구분 ID")
    user_name: str = Field(max_length=16, description="유저명")
    phone: Optional[str] = Field(max_length=11, nullable=True, description="연락처")
    address: Optional[str] = Field(max_length=128, nullable=True, description="주소")
    emergency_contact: Optional[str] = Field(max_length=11, nullable=True, description="긴급 연락처")

    is_caregiver: bool = Field(default=False, description="보호자 여부")
    is_helper: bool = Field(default=False, description="도우미 여부")

    # 관계
    user: User = Relationship(back_populates="profile")


class UserAlert(TimestampMixin, table=True):
    """사용자 알림 설정"""
    __tablename__ = "users_alert"
    
    user_id: int = Field(primary_key=True, foreign_key="users.user_id", description="유저 구분 ID")
    fcm_token: Optional[str] = Field(default=None, max_length=64, description="FCM 토큰")
    is_alert: bool = Field(default=False, description="알림 유무, default: False")
    
    # 관계
    user: User = Relationship(back_populates="alert")