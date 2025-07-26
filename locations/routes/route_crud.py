

from typing import List
from fastapi import HTTPException
from sqlmodel import Session, select
from common.postgres.crud.base import CRUDBase
from .route import RouteHistory


class CRUDRouteHistory(CRUDBase[RouteHistory, None, None]):
    """경로 탐색 기록 CRUD"""
    def get_by_user_id(self, db: Session, user_id: int) -> List[RouteHistory]:
        return db.exec(select(RouteHistory).where(RouteHistory.user_id == user_id)).all()

    def get_by_route_id(self, db: Session, route_id: int) -> RouteHistory:
        return db.exec(select(RouteHistory).where(RouteHistory.route_id == route_id)).first()

    def create_route_history(self, db: Session, route_history: RouteHistory) -> RouteHistory:
        db.add(route_history)
        db.commit()
        db.refresh(route_history)
        return route_history

    def delete_route_history(self, db: Session, route_id: int) -> RouteHistory:
        route_history = db.exec(select(RouteHistory).where(RouteHistory.route_id == route_id)).first()
        if not route_history:
            raise HTTPException(status_code=404, detail=f"Route history with route_id {route_id} not found")
        db.delete(route_history)
        db.commit()
        return route_history


route_history_crud = CRUDRouteHistory(RouteHistory)