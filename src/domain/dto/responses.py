from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    message: str

class MessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    received_message: str
    response: str