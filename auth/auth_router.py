import os
from datetime import datetime, timedelta, timezone

# import httpx
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
# from fastapi.requests import Request
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose import jwt, JWTError

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.memcache.database import memcache_client
from common.postgres.database import get_session
from users.user import User
from users.user_crud import user_crud

from .dto import LoginReqDto

router = APIRouter(tags=["Auth API"])


SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")
SUPABASE_JWKS_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co/auth/v1/.well-known/jwks.json"
SUPABASE_AUDIENCE = f"https://{SUPABASE_PROJECT_ID}.supabase.co/auth/v1"

SERVER_JWT_SECRET = os.getenv("SERVER_JWT_SECRET")
SERVER_JWT_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 서버 JWT 발급
def create_server_jwt(user_id: str, email: str):
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(payload, SERVER_JWT_SECRET, algorithm=SERVER_JWT_ALGORITHM)
    return token

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not (user := memcache_client.get(token)):
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# Supabase JWT 검증
async def verify_supabase_jwt(token: str):
    # async with httpx.AsyncClient() as client:
    #     jwks_response = await client.get(SUPABASE_JWKS_URL)
    #     jwks = jwks_response.json()["keys"]

    # for key in jwks:
    #     try:
    #         public_key = jwt.construct_rsa_public_key(key)
    #         payload = jwt.decode(token, public_key, algorithms=["RS256"], audience=SUPABASE_AUDIENCE)
    #         return payload  # 검증 성공
    #     except JWTError:
    #         continue

    # 서버에서 직접 시크릿 키로 Supabase JWT를 해제(검증)하는 로직
    try:
        # 환경 변수에서 Supabase JWT 시크릿 키를 가져옴
        supabase_jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        if not supabase_jwt_secret:
            raise HTTPException(status_code=500, detail="Supabase JWT 시크릿이 설정되지 않았습니다.")

        # JWT를 직접 해독 및 검증 (audience 포함)
        payload = jwt.decode(
            token,
            supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload  # 검증 성공 시 payload 반환
    except JWTError:
        # JWT 해독 실패 시 예외 처리
        raise HTTPException(status_code=401, detail=f"Invalid token")

    # raise HTTPException(status_code=401, detail="Invalid Supabase token")

@router.post("/login")
async def login(login_req: LoginReqDto, db: Session = Depends(get_session)):
    supabase_token = login_req.access_token
    if not supabase_token:
        raise HTTPException(status_code=400, detail="Missing access_token")

    payload = await verify_supabase_jwt(supabase_token)
    openid = payload["sub"]
    platform = payload["app_metadata"]["provider"]
    email = payload.get("email")

    # 서버 JWT 발급
    flag = False
    if not (user := user_crud.get_by_oauth(db, platform, openid)):
        user = user_crud.create_user(db, User(platform=platform, openid=openid))
        flag = True

    memcache_client.set(supabase_token, user, expire=60*60)
    if flag:
        # 회원가입 처리
        return JSONResponse(status_code=201, content={"message": "회원가입 완료"})
    else:
        return JSONResponse(status_code=200, content={"message": "로그인 완료"})

@router.delete("/logout")
async def logout(user: User = Depends(get_current_user)):
    memcache_client.delete("authorized_user:" + str(user.user_id))
    return {"message": "Logout"}