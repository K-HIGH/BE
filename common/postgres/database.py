"""
데이터베이스 설정 및 연결 관리

PostgreSQL 데이터베이스 연결과 세션 관리를 담당
"""

import os
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.orm import sessionmaker

# 환경변수에서 데이터베이스 설정 가져오기
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "k-high")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 엔진 생성
engine = create_engine(
    DATABASE_URL,
    echo=True,  # SQL 쿼리 로깅 (개발 환경에서만 사용)
    pool_pre_ping=True,  # 연결 상태 확인
    pool_recycle=300,  # 5분마다 연결 재생성
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db_and_tables():
    """데이터베이스와 테이블 생성"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """데이터베이스 세션 생성기"""
    with SessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# 데이터베이스 초기화 함수
def init_db():
    """데이터베이스 초기화"""
    create_db_and_tables()
    print("데이터베이스 테이블이 생성되었습니다.") 