"""
기본 CRUD 클래스

모든 CRUD 작업에서 공통으로 사용하는 기본 클래스
"""

from typing import Generic, TypeVar, Type, Optional, List, Any, Dict, Union
from sqlmodel import SQLModel, select, Session
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    기본 CRUD 클래스
    
    모든 모델에 대한 기본적인 CRUD 작업을 제공합니다.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        CRUD 객체 초기화
        
        Args:
            model: SQLModel 클래스
        """
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """ID로 단일 객체 조회"""
        statement = select(self.model).where(self.model.id == id)
        return db.exec(statement).first()
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """여러 객체 조회 (페이지네이션)"""
        statement = select(self.model).offset(skip).limit(limit)
        return list(db.exec(statement))
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """새 객체 생성"""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """객체 업데이트"""
        obj_data = db_obj.model_dump()
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> ModelType:
        """객체 삭제"""
        obj = db.get(self.model, id)
        db.delete(obj)
        db.commit()
        return obj 