from fastapi import APIRouter
from src.domain.dto.responses import HealthResponse, MessageRequest, MessageResponse
from typing import Dict

root_router = APIRouter()


# 기본 라우트
@root_router.get("/")
async def root() -> Dict[str, str]:
    """루트 엔드포인트"""
    return {"message": "K-HI Backend API에 오신 것을 환영합니다!"}

# 헬스 체크 엔드포인트
@root_router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """서버 상태를 확인하는 헬스체크 엔드포인트"""
    return HealthResponse(
        status="healthy",
        message="서버가 정상적으로 작동하고 있습니다."
    )

# 예시 POST 엔드포인트
@root_router.post("/message", response_model=MessageResponse)
async def send_message(request: MessageRequest) -> MessageResponse:
    """메시지를 받아서 응답을 반환하는 예시 엔드포인트"""
    return MessageResponse(
        received_message=request.message,
        response=f"받은 메시지: '{request.message}'에 대한 응답입니다."
    )