from typing import Optional
from pydantic import BaseModel


class UserAlertUpdateRes(BaseModel):
    fcm_token: Optional[str] = None
    is_alert: bool