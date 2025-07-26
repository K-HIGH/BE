"""
기본 모델 클래스

모든 모델에서 공통으로 사용하는 기본 클래스와 타입 정의
"""

from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field
from pydantic import BaseModel


class TimestampMixin(SQLModel):
    """타임스탬프 믹스인"""
    created_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"default": datetime.now})
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"default": datetime.now, "onupdate": datetime.now})


class OAuthPlatform(str, Enum):
    """OAuth 플랫폼 열거형"""
    KAKAO = "kakao"
    GOOGLE = "google"
    APPLE = "apple"
    NAVER = "naver"


class Point(BaseModel):
    """PostgreSQL POINT 타입을 위한 모델"""
    x: float  # 경도 (longitude)
    y: float  # 위도 (latitude)
    
    def __str__(self) -> str:
        return f"({self.x},{self.y})"
    
    @classmethod
    def from_string(cls, point_str: str) -> "Point":
        """문자열에서 Point 객체 생성"""
        # PostgreSQL POINT 형식: "(x,y)" 또는 "x,y"
        point_str = point_str.strip("()")
        x, y = map(float, point_str.split(","))
        return cls(x=x, y=y) 