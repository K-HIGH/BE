from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from users.user_dto import UserViewRes


class CaregiverGetRes(BaseModel):
    caregiver_id: int
    user_ulid: str
    target_ulid: str
    created_at: datetime
    updated_at: datetime

class CaregiverGetResWithTarget(BaseModel):
    caregiver_id: int
    user_ulid: str
    target_ulid: str
    created_at: datetime
    updated_at: datetime
    target: Optional[UserViewRes] = None

class TakerApproveReq(BaseModel):
    caregiver_id: int
    is_approved: bool

class CaregiverCreateReq(BaseModel):
    target_email: str

class CaregiverUpdateReq(BaseModel):
    relationship_type: Optional[str] = None
    description: Optional[str] = None