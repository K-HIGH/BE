from typing import Optional
from common.postgres.models.base import OAuthPlatform
from pydantic import BaseModel
from users.user import User, UserAlert, UserProfile


class UserProfileAlertRes(BaseModel):
    user_name: str
    phone: Optional[str] = None
    is_caregiver: Optional[bool] = None
    is_helper: Optional[bool] = None
    fcm_token: Optional[str] = None
    is_alert: bool

class UserProfileUpdateReq(BaseModel):
    user_name: Optional[str] = None
    phone: Optional[str] = None
    is_caregiver: Optional[bool] = None
    is_helper: Optional[bool] = None

class UserProfileRes(BaseModel):
    user_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    is_caregiver: Optional[bool] = None
    is_helper: Optional[bool] = None

class UserAlertRes(BaseModel):
    fcm_token: Optional[str] = None
    is_alert: bool

class UserRes(BaseModel):
    user: User
    user_profile: UserProfileRes
    user_alert: UserAlertRes

class UserViewRes(BaseModel):
    user_id: int
    user_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None