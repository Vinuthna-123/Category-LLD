import logging
from typing import Type, TypeVar, Generic, Optional, List, Dict, Any, Union
from sqlalchemy import Column, desc, asc
from sqlalchemy.orm import DeclarativeBase, Session
from base.repository.constants.constants import TABLE_TO_PK_PREFIX
from base.utils.id.short_id import generate_primary_key

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=DeclarativeBase)

class BaseRepository(Generic[T]):
    def __init__(self, db: Session):
        self.db = db

    def _get_prefix(self, model_instance: T) -> str:
        for cls, prefix in TABLE_TO_PK_PREFIX.items():
            if isinstance(model_instance, cls):
                return prefix
        raise ValueError(f"No prefix defined for model {type(model_instance)}")

    def _generate_id(self, prefix: str) -> str:
        return generate_primary_key(prefix)

    def get_by_id(self, model: Type[T], id: str) -> Optional[T]:
        return self.db.get(model, id)

    def _to_serializable(self, value):
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        return value

    def _model_to_dict(self, model) -> Dict[str, Any]:
        return {
            column.name: self._to_serializable(getattr(model, column.name))
            for column in model.__table__.columns
        }

    def _row_to_dict(self, row_data, columns: List[Column]) -> Dict[str, Any]:
        if len(columns) == 1:
            return {columns[0].name: self._to_serializable(row_data)}
        return {
            col.name: self._to_serializable(row_data[i])
            for i, col in enumerate(columns)
        }

    def apply_filters(self, query, model: Type[T], filters: Dict[str, Any]):
        for field_name, condition in filters.items():
            column = getattr(model, field_name, None)
            if column is None:
                continue
            if isinstance(condition, dict):
                for op, val in condition.items():
                    if op == "eq":
                        query = query.filter(column == val)
                    elif op == "in":
                        query = query.filter(column.in_(val))
                    elif op == "nin":
                        query = query.filter(~column.in_(val))
                    elif op == "gt":
                        query = query.filter(column > val)
                    elif op == "gte":
                        query = query.filter(column >= val)
                    elif op == "lt":
                        query = query.filter(column < val)
                    elif op == "lte":
                        query = query.filter(column <= val)
                    elif op == "like":
                        query = query.filter(column.like(val))
                    elif op == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
                        query = query.filter(column.between(val[0], val[1]))
                    else:
                        logger.warning(f"Unsupported filter operation: {op}")
            else:
                query = query.filter(column == condition)
        return query

    def apply_sorting(self, query, model: Type[T], sort_specs: List[Dict[str, Any]]):
        for spec in sort_specs:
            field = spec.get("field")
            order = spec.get("order", "asc")
            if field and order in ("asc", "desc"):
                column = getattr(model, field, None)
                if column is not None:
                    query = query.order_by(desc(column) if order == "desc" else asc(column))
        return query

    def list(
        self,
        model: Type[T],
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[List[Dict[str, Any]]] = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:

        if columns:
            sqlalchemy_columns = [getattr(model, col) for col in columns]
            query = self.db.query(*sqlalchemy_columns)
        else:
            query = self.db.query(model)

        # Soft delete
        if not include_deleted and hasattr(model, "is_deleted"):
            if not filters:
                filters = {}
            if "is_deleted" not in filters:
                filters["is_deleted"] = {"eq": False}

  
        if filters:
            query = self.apply_filters(query, model, filters)
        total_count = query.count()

        #Sorting
        if sort_by:
            query = self.apply_sorting(query, model, sort_by)

        # Pagination
        query_data = query.offset(skip).limit(limit).all()

        # Convert to dict
        if columns:
            sqlalchemy_columns = [getattr(model, col) for col in columns]
            data = [self._row_to_dict(row, sqlalchemy_columns) for row in query_data]
        else:
            data = [self._model_to_dict(item) for item in query_data]

        return {
            "data": data,
            "total_count": total_count
        }

    def create(self, model_instance: Union[T, List[T]]) -> Union[str, List[str]]:
        if isinstance(model_instance, list):
            ids = []
            for instance in model_instance:
                if getattr(instance, "id", None):
                    raise ValueError("Model instance already has an ID.")
                prefix = self._get_prefix(instance)
                instance.id = self._generate_id(prefix)
                self.db.add(instance)
                ids.append(instance.id)
            self.db.commit()
            return ids
        else:
            if getattr(model_instance, "id", None):
                raise ValueError("Model instance already has an ID.")
            prefix = self._get_prefix(model_instance)
            model_instance.id = self._generate_id(prefix)
            self.db.add(model_instance)
            self.db.commit()
            return model_instance.id

    def get_one(self, model: Type[T], filters: Dict[str, Any]) -> Optional[T]:
        query = self.db.query(model)
        for attr, value in filters.items():
            if hasattr(model, attr):
                query = query.filter(getattr(model, attr) == value)
        return query.first()

    def update(self, model: Type[T], id: str, update_data: Dict[str, Any]) -> Optional[T]:
        instance = self.get_by_id(model, id)
        if not instance:
            return None
        for key, value in update_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        self.db.commit()
        return instance

    def update_one_by_id(self, model: Type[T], record_id: str, fields_to_update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        instance = self.get_by_id(model, record_id)
        if not instance:
            return None
        for key, value in fields_to_update.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance.__dict__

    def delete(self, model: Type[T], id: str) -> bool:
        instance = self.get_by_id(model, id)
        if instance:
            self.db.delete(instance)
            self.db.commit()
            return True
        return False
