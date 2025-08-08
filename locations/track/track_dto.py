

from pydantic import BaseModel


class TrackUpdateReq(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    speed: float
    direction: float


class TrackGetRes(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    speed: float
    direction: float