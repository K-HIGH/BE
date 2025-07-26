

from pydantic import BaseModel


class UserProfileUpdateRes(BaseModel):
    user_name: str
    phone: str
    is_caregiver: bool
    is_helper: bool