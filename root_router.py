from fastapi import APIRouter
from common.basic_dtos.responses import MessageResponse
from common.basic_dtos.requests import MessageRequest

from users import router as users_router
from auth import router as auth_router
from locations import router as locations_router


root_router = APIRouter(prefix="/api/v1")


# 예시 POST 엔드포인트
@root_router.post("/message", response_model=MessageResponse, tags=["Root"])
async def send_message(request: MessageRequest) -> MessageResponse:
    """메시지를 받아서 응답을 반환하는 예시 엔드포인트"""
    return MessageResponse(
        received_message=request.message,
        response=f"받은 메시지: '{request.message}'에 대한 응답입니다."
    )