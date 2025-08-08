

from typing import Union
from pydantic import BaseModel


class TrackUpdateReq(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    speed: float
    direction: float


class TrackGetRes(BaseModel):
    latitude: Union[float, None]
    longitude: Union[float, None]
    altitude: Union[float, None]
    speed: Union[float, None]
    direction: Union[float, None]