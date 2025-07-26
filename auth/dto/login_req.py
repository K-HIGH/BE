from pydantic import BaseModel


class LoginReqDto(BaseModel):
    """로그인 요청 DTO"""
    access_token: str