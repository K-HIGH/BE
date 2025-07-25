from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.responses import JSONResponse

from root_router import root_router


# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="K-HIGH Backend API",
    description="""
    # K-HIGH 프로젝트 백엔드 API
    
    ## 주요 기능
    - 사용자 인증 및 관리
    - 위치 기반 서비스
    - 경로 탐색 및 기록
    - 도우미 관리
    
    ## API 문서
    - **Swagger UI**: `/docs` - 인터랙티브 API 문서
    - **ReDoc**: `/redoc` - 대안 API 문서
    - **OpenAPI JSON**: `/openapi.json` - OpenAPI 스펙
    
    ## 개발 정보
    - **버전**: 1.0.0
    - **개발자**: K-HIGH Team
    """,
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 경로
    redoc_url="/redoc",  # ReDoc 경로
    openapi_url="/openapi.json",  # OpenAPI 스펙 경로
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # 모델 섹션 접기
        "defaultModelExpandDepth": 1,    # 모델 상세 정보 기본 접기
        "displayRequestDuration": True,   # 요청 시간 표시
        "docExpansion": "list",          # API 그룹 기본 펼침
        "filter": True,                  # 검색 필터 활성화
        "showExtensions": True,          # 확장 정보 표시
        "showCommonExtensions": True,    # 공통 확장 정보 표시
        "tryItOutEnabled": True,         # Try it out 기능 활성화
    }
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(root_router)

# 기본 라우트
@app.get("/", tags=["Root"])
async def root() -> JSONResponse:
    """
    루트 엔드포인트
    
    서버 상태 확인 및 API 문서 링크 제공
    """
    return JSONResponse(
        content={
            "message": "K-HIGH Backend API 서버가 정상적으로 실행 중입니다.",
            "version": "1.0.0",
            "docs": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_json": "/openapi.json"
            }
        }
    )

# 헬스 체크 엔드포인트
@app.get("/health", tags=["Root"])
async def health_check() -> JSONResponse:
    """서버 상태를 확인하는 헬스체크 엔드포인트"""
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    )

# 서버 실행 (개발용)
if __name__ == "__main__":
    print("🚀 K-HIGH Backend API 서버를 시작합니다...")
    print("📖 API 문서:")
    print("   - Swagger UI: http://localhost:8001/docs")
    print("   - ReDoc: http://localhost:8001/redoc")
    print("   - OpenAPI JSON: http://localhost:8001/openapi.json")
    print("🌐 서버 주소: http://localhost:8001")
    print("=" * 50)
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,  # 개발 모드에서 코드 변경시 자동 재시작
        log_level="info"
    ) 