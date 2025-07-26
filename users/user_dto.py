from typing import Optional
from pydantic import BaseModel


class UserProfileAlertRes(BaseModel):
    user_name: str
    phone: str
    is_caregiver: bool
    is_helper: bool
    fcm_token: Optional[str] = None
    is_alert: bool

class UserProfileUpdateReq(BaseModel):
    user_name: str
    phone: str
    is_caregiver: bool
    is_helper: bool

class UserProfileUpdateRes(BaseModel):
    user_name: str
    phone: str
    is_caregiver: bool
    is_helper: bool

class UserAlertUpdateRes(BaseModel):
    fcm_token: Optional[str] = None
    is_alert: bool