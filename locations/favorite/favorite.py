"""
즐겨찾기 위치 모델

사용자가 즐겨찾기한 위치 정보를 관리하는 모델
"""

from typing import Optional, Dict, Any
from sqlalchemy import Column
from geoalchemy2 import Geometry

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field, Relationship

from common.postgres.models import TimestampMixin


class LocationFavorite(SQLModel, TimestampMixin, table=True):
    """즐겨찾기 위치 정보"""
    __tablename__ = "loc_favorite"
    
    location_id: Optional[int] = Field(default=None, primary_key=True, description="즐겨찾기 장소 ID")
    user_id: int = Field(foreign_key="users.user_id", description="유저 구분 ID")
    loc_name: str = Field(max_length=16, description="장소명")
    loc_coor: str = Field(
        sa_column=Column(Geometry(geometry_type="POINT", srid=4326)),
        description="장소 좌표"
    )
    loc_desc: str = Field(max_length=64, description="장소 설명")
    loc_info: Dict[str, Any] = Field(
        sa_column=Column(JSONB),
        description="장소 정보"
    )
    
    # 관계
    user: "User" = Relationship(back_populates="favorites")