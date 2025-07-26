"""
보호자 관련 모델

보호자 정보와 위치 캐시를 관리하는 모델
"""

from typing import Optional
from sqlmodel import Field, Relationship

from common.postgres.models import TimestampMixin


class Caregiver(TimestampMixin, table=True):
    """보호자 정보"""
    __tablename__ = "caregivers"
    
    user_id: int = Field(primary_key=True, foreign_key="users.user_id", description="보호자 ID")
    target_id: int = Field(foreign_key="users.user_id", description="보호 대상 ID")

    # 관계
    user: Optional["User"] = Relationship(
        back_populates="caregivers",
        sa_relationship_kwargs={"foreign_keys": "[Caregiver.user_id]"}
    )
    target_user: Optional["User"] = Relationship(
        back_populates="target_caregivers",
        sa_relationship_kwargs={"foreign_keys": "[Caregiver.target_id]"}
    )
