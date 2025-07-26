from pydantic import BaseModel


class UserProfileUpdateReq(BaseModel):
    user_name: str
    phone: str
    is_caregiver: bool
    is_helper: bool