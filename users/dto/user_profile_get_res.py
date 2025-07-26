

from pydantic import BaseModel


class UserProfileGetRes(BaseModel):
    user_name: str
    phone: str
    is_caregiver: bool
    is_helper: bool