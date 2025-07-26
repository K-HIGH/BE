from pydantic import BaseModel


class SafetyAreaGetRes(BaseModel):
    safety_area_id: int
    safety_area_name: str
    loc_safety_area: str
    dist_safety_radius: float

class SafetyAreaCreateReq(BaseModel):
    safety_area_name: str
    loc_safety_area: str
    dist_safety_radius: float

class SafetyAreaUpdateReq(BaseModel):
    safety_area_name: str
    loc_safety_area: str
    dist_safety_radius: float