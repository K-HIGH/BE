from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.domain.root_router import root_router


# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="K-HIGH Backend API",
    description="K-HIGH 프로젝트의 백엔드 API입니다.",
    version="1.0.0"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router)

# 서버 실행 (개발용)
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,  # 개발 모드에서 코드 변경시 자동 재시작
        log_level="info"
    ) 