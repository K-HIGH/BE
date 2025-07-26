"""
경로 관련 모델

사용자의 경로 탐색 기록을 관리하는 모델
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from sqlmodel import Field, Relationship

from common.postgres.models import TimestampMixin


class RouteHistory(TimestampMixin, table=True):
    """사용자 경로 탐색 기록"""
    __tablename__ = "route_history"
    
    route_id: int = Field(primary_key=True, description="경로 탐색 기록 ID")
    user_id: int = Field(foreign_key="users.user_id", description="유저 구분 ID")
    
    # 경로 정보
    src: Dict[str, Any] = Field(
        sa_column=Column(JSONB),
        description="JSONB, 출발지 정보"
    )
    dst: Dict[str, Any] = Field(
        sa_column=Column(JSONB),
        description="JSONB, 도착지 정보"
    )
    routes: Dict[str, Any] = Field(
        sa_column=Column(JSONB),
        description="JSONB, 경로 정보"
    )
    
    # 관계
    user: "User" = Relationship(back_populates="route_histories") 