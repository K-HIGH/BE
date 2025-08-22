import os
from datetime import datetime, timedelta, timezone

# import httpx
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import HTTPException
# from fastapi.requests import Request
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose import jwt, JWTError

from fastapi import APIRouter, Depends
from sqlmodel import Session

from common.memcache.database import memcache_client
from common.postgres.database import get_session
from users.user import User, UserAlert, UserProfile
from users.user_crud import user_crud, user_profile_crud, user_alert_crud
from users.user_dto import UserAlertRes, UserRes, UserProfileRes

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

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_session)
):
    
    payload = await verify_supabase_jwt(token)
    openid = payload["sub"]
    platform = payload["app_metadata"]["provider"]
    email = payload.get("email")

    key = f"oauth:{platform}:{openid}"
    if user := memcache_client.get(key):
        user = db.merge(user)
        return user

    if not (user := user_crud.get_by_oauth(db, platform, openid)):
        raise HTTPException(status_code=401, detail="Invalid token")

    memcache_client.set(key, user, expire=60*60)
    
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
    except JWTError as e:
        # JWT 해독 실패 시 예외 처리
        print(f"JWTError: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid token")

@router.post("/login")
async def login(
    login_req: LoginReqDto, 
    db: Session = Depends(get_session)
):
    supabase_token = login_req.access_token
    if not supabase_token:
        raise HTTPException(status_code=400, detail="Missing access_token")

    payload = await verify_supabase_jwt(supabase_token)
    openid = payload["sub"]
    platform = payload["app_metadata"]["provider"]
    user_name = payload["user_metadata"]["name"]
    email = payload.get("email")

    flag = False
    if not (user := user_crud.get_by_oauth(db, platform, openid)):
        user = user_crud.create_user(db, User(oauth_platform=platform, openid=openid, email=email))
        user_profile = user_profile_crud.create_user_profile(db, UserProfile(user_id=user.user_id, user_name=user_name))
        user_alert = user_alert_crud.create_user_alert(db, UserAlert(user_id=user.user_id, is_alert=False))
        flag = True
    else:
        user_profile = user_profile_crud.get_by_user_id(db, user.user_id)
        user_alert = user_alert_crud.get_by_user_id(db, user.user_id)

    key = f"oauth:{platform}:{openid}"
    memcache_client.set(key, user, expire=60*60)
    if flag:
        # 회원가입 처리
        return JSONResponse(
            status_code=201, 
            content=UserRes(
                user=user,
                user_profile=UserProfileRes(
                    user_name=user_name,
                    phone=user_profile.phone,
                    is_caregiver=user_profile.is_caregiver,
                    is_helper=user_profile.is_helper
                ),
                user_alert=UserAlertRes(
                    fcm_token=user_alert.fcm_token,
                    is_alert=user_alert.is_alert
                )
            ).model_dump(mode="json"))

    else:
        return JSONResponse(
            status_code=200, 
            content=UserRes(
                user=user,
                user_profile=UserProfileRes(
                    user_name=user_name,
                    phone=user_profile.phone,
                    is_caregiver=user_profile.is_caregiver,
                    is_helper=user_profile.is_helper
                ),
                user_alert=UserAlertRes(
                    fcm_token=user_alert.fcm_token,
                    is_alert=user_alert.is_alert
                )
            ).model_dump(mode="json"))

@router.post("/token")
async def token(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    user_profile = user_profile_crud.get_by_user_id(db, user.user_id)
    user_alert = user_alert_crud.get_by_user_id(db, user.user_id)
    return JSONResponse(
        status_code=200, 
        content=UserRes(
            user=user,
            user_profile=UserProfileRes(
                user_name=user_profile.user_name,
                phone=user_profile.phone,
                is_caregiver=user_profile.is_caregiver,
                is_helper=user_profile.is_helper
            ),
            user_alert=UserAlertRes(
                fcm_token=user_alert.fcm_token,
                is_alert=user_alert.is_alert
            )
        ).model_dump(mode="json"))

@router.delete("/logout")
async def logout(user: User = Depends(get_current_user)):
    key = f"oauth:{user.oauth_platform}:{user.openid}"
    memcache_client.delete(key)
    return Response(status_code=204)