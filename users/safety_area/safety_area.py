"""
안전 구역 관련 모델

사용자가 정의한 안전 구역을 관리하는 모델
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import POINT

from sqlmodel import SQLModel, Field, Relationship

from common.postgres.models import TimestampMixin, Point


class SafetyArea(SQLModel, TimestampMixin, table=True):
    """안전 구역 정보"""
    __tablename__ = "safety_area"
    
    safety_area_id: Optional[int] = Field(default=None, primary_key=True, description="안전 구역 ID")
    user_id: int = Field(foreign_key="users.user_id", description="유저 구분 ID")
    safety_area_name: str = Field(max_length=32, description="안전 구역명")
    loc_safety_area: Point = Field(
        sa_column=Column(POINT),
        description="안전 구역 중심 좌표"
    )
    dist_safety_area: float = Field(description="안전 구역 반지름")
    updated_at: Optional[datetime] = Field(default=None, description="수정 시각")
    
    # 관계
    user: "User" = Relationship(back_populates="safety_areas") 