

from typing import Optional
from pydantic import BaseModel


class LocationFavoriteRes(BaseModel):
    location_id: int
    loc_name: str
    loc_coor: str
    loc_desc: str
    loc_info: dict

class LocationFavoriteCreateReq(BaseModel):
    loc_name: str
    loc_coor: str
    loc_desc: str
    loc_info: dict

class LocationFavoriteUpdateReq(BaseModel):
    loc_name: Optional[str] = None
    loc_coor: Optional[str] = None
    loc_desc: Optional[str] = None
    loc_info: Optional[dict] = None