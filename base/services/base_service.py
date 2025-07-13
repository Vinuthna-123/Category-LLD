import logging
from typing import Any, Dict, List, Optional, Type , TypeVar
from abc import ABC, abstractmethod
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session , DeclarativeBase
from base.repository.base_repo import BaseRepository
from base.schema.request import DateRange, FilterExpression, Pagination, SortBy, BaseFilters

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=DeclarativeBase)

class BaseService(ABC):
    def __init__(self, db: Session):
        self.db = db
        self.repository: BaseRepository = self._get_repository()

    @abstractmethod 
    # any class that is inherit from this baseservice must implement this method
    def _get_repository(self) -> BaseRepository:
        pass

    def convert_single_to_sqlalchemy(self, pydantic_obj: BaseModel, model_class: Type) -> Any:
        data = pydantic_obj.model_dump(exclude_none=True)
        return model_class(**data)

    def convert_to_sqlalchemy(self, pydantic_objects: List[Any], model_class: Type) -> List[Any]:
        return [self.convert_single_to_sqlalchemy(obj, model_class) for obj in pydantic_objects]

    def list(self,model_class: Type,pagination: Pagination,sort_by: List[SortBy] = None,filters: Optional[BaseFilters] = None,include_deleted: Optional[bool] = False,columns: Optional[List] = None) -> Dict[str, Any]:
        try:
            page, limit = self.validate_pagination(pagination.page, pagination.limit)
            offset = pagination.offset
            processed_filters = self.process_filters(filters)
            sort_by = self.process_sort_by(sort_by)
            
            return self.repository.list(
                model=model_class,
                filters=processed_filters,
                sort_by=sort_by,
                skip=offset,
                limit=limit,
                include_deleted=include_deleted,
                columns=columns
            )
        except Exception as e:
            logging.exception(str(e))
            logger.error(f"Error in {self.__class__.__name__}.list: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def validate_pagination(self, page: int, limit: int) -> tuple[int, int]:
        page = max(1, page)
        limit = min(max(1, limit), 1000)
        return page, limit

    def process_sort_by(self, sort_by: List[SortBy]) -> List[Optional[Dict[str, Any]]]:
        if not sort_by:
            return []
        processed_sort = []
        for sort_spec in sort_by:
            field = sort_spec.field
            order = sort_spec.order
            processed_sort.append({
                "field": field,
                "order": order
            })
        return processed_sort

    def process_filters(self, filters: BaseFilters) -> Dict[Any, Dict[str, Any]]:
        if not filters:
            return {}
        
        processed_filters = {}
        for field_name in filters.__annotations__:
            if hasattr(filters, field_name):
                field_value = getattr(filters, field_name) 
                if field_value is None:
                    continue
                if isinstance(field_value, FilterExpression):
                    processed_filters[field_name] = {"op": field_value.op, "value": field_value.value}
                    print(f"Processed filter: {field_name} -> {processed_filters[field_name]}")
                elif isinstance(field_value, DateRange):
                    processed_filters[field_name] = {
                        "op": "between",
                        "value": [field_value.from_, field_value.to]
                    }
        return processed_filters
    

    def get_by_id(self, model_class: Type, record_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.repository.get_by_id(model_class, record_id)
        except Exception as e:
            logger.exception(f"{self.__class__.__name__}.get_by_id: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_one(self, model_class: Type, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            return self.repository.get_one(model_class, filters)
        except Exception as e:
            logger.exception(f"{self.__class__.__name__}.get_one: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def create(self, model_class: Type, pydantic_objects: List[BaseModel]) -> List[str]:
        try:
            sqlalchemy_objects = self.convert_to_sqlalchemy(pydantic_objects, model_class)
            return self.repository.create(sqlalchemy_objects, model_class)
        except Exception as e:
            logger.exception(f"{self.__class__.__name__}.create: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def create_one(self, model_class: Type, pydantic_obj: BaseModel) -> str:
        try:
            sqlalchemy_obj = self.convert_single_to_sqlalchemy(pydantic_obj, model_class)
            created_ids = self.repository.create([sqlalchemy_obj])
            return created_ids[0]
        except Exception as e:
            logger.exception(f"{self.__class__.__name__}._create_one: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def update_by_id(self,model_class: Type,record_id: str,fields_to_update: BaseModel) -> Optional[Dict[str, Any]]:
        try:
            sqlalchemy_obj = self.convert_single_to_sqlalchemy(fields_to_update, model_class)
            return self.repository.update_one_by_id(model_class, record_id, sqlalchemy_obj)
        except Exception as e:
            logger.exception(f"{self.__class__.__name__}.update_by_id: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def update_one(self,model_class: Type,filters: Dict[str, Any],fields_to_update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            return self.repository.update_one(model_class, filters, fields_to_update)
        except Exception as e:
            logger.exception(f"{self.__class__.__name__}.update_one: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def update_all(self, model_class: Type, pydantic_objects: List[BaseModel]) -> List[str]:
        try:
            sqlalchemy_objects = self.convert_to_sqlalchemy(pydantic_objects, model_class)
            return self.repository.update_all(sqlalchemy_objects, model_class)
        except Exception as e:
            logger.exception(f"{self.__class__.__name__}.update_all: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def delete_by_id(self, model_class: Type, record_id: str) -> int:
        try:
            return self.repository.delete_by_id(model_class, record_id)
        except Exception as e:
            logger.exception(f"{self.__class__.__name__}.delete_by_id: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def delete(self, model_class: Type, filters: Dict[str, Any]) -> int:
        try:
            return self.repository.delete(model_class, filters)
        except Exception as e:
            logger.exception(f"{self.__class__.__name__}.delete: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
