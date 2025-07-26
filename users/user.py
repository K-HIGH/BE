"""
사용자 관련 모델

사용자 정보, 프로필, 알림 설정을 관리하는 모델
"""

import uuid
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, ENUM

from sqlmodel import SQLModel, Field, Relationship

from common.postgres.models.base import TimestampMixin, OAuthPlatform


class User(SQLModel, TimestampMixin, table=True):
    """사용자 기본 정보"""
    __tablename__ = "users"
    
    user_id: Optional[int] = Field(default=None, primary_key=True, description="유저 구분 ID, jwt 토큰 부여 시 사용")
    user_uuid: uuid.UUID = Field(
        default_factory=uuid.uuid4, 
        sa_column=Column(UUID(as_uuid=True), unique=True, index=True),
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
    
    # 관계
    profile: Optional["UserProfile"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    alert: Optional["UserAlert"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    favorites: list["LocationFavorite"] = Relationship(back_populates="user")
    route_histories: list["RouteHistory"] = Relationship(back_populates="user")
    caregivers: list["Caregiver"] = Relationship(back_populates="user")
    target_caregivers: list["Caregiver"] = Relationship(back_populates="target_user")
    safety_areas: list["SafetyArea"] = Relationship(back_populates="user")


class UserProfile(SQLModel, TimestampMixin, table=True):
    """사용자 프로필 정보"""
    __tablename__ = "users_profile"
    
    user_id: int = Field(primary_key=True, foreign_key="users.user_id", description="유저 구분 ID")
    user_name: str = Field(max_length=16, description="유저명")
    phone: str = Field(max_length=11, description="연락처")
    is_caregiver: bool = Field(default=False, description="보호자 여부")
    is_helper: bool = Field(default=False, description="도우미 여부")
    
    # 관계
    user: User = Relationship(back_populates="profile")


class UserAlert(SQLModel, table=True):
    """사용자 알림 설정"""
    __tablename__ = "users_alert"
    
    user_id: int = Field(primary_key=True, foreign_key="users.user_id", description="유저 구분 ID")
    fcm_token: Optional[str] = Field(default=None, max_length=64, description="FCM 토큰")
    is_alert: bool = Field(default=False, description="알림 유무, default: False")
    
    # 관계
    user: User = Relationship(back_populates="alert") 