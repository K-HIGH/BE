

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel

from common.tmap.api_client import TmapCoordinate


class RouteHistoryRes(BaseModel):
    route_id: int
    user_id: int
    src: Dict[str, Any]
    dst: Dict[str, Any]
    routes: Dict[str, Any]
    created_at: datetime
    

class RouteReq(BaseModel):
    src: TmapCoordinate
    dst: TmapCoordinate
    count: int = 3