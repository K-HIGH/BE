from datetime import datetime
from pydantic import BaseModel


class CaregiverGetRes(BaseModel):
    caregiver_id: int
    user_id: int
    target_id: int
    created_at: datetime
    updated_at: datetime

class TakerApproveReq(BaseModel):
    caregiver_id: int
    is_approved: bool
