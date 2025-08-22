from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from users.user_dto import UserViewRes


class CaregiverGetRes(BaseModel):
    caregiver_id: int
    user_id: int
    target_id: int
    created_at: datetime
    updated_at: datetime

class CaregiverGetResWithTarget(BaseModel):
    caregiver_id: int
    user_id: int
    target_id: int
    created_at: datetime
    updated_at: datetime
    target: Optional[UserViewRes] = None

class TakerApproveReq(BaseModel):
    caregiver_id: int
    is_approved: bool

class CaregiverUpdateReq(BaseModel):
    relationship_type: Optional[str] = None
    description: Optional[str] = None