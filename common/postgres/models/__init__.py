"""
데이터베이스 모델 패키지

PostgreSQL과 SQLModel을 사용한 데이터베이스 스키마 정의
"""

from .base import TimestampMixin, OAuthPlatform

__all__ = [
    "TimestampMixin",
    "OAuthPlatform",
] 