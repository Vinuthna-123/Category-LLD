from typing import Generic, Optional, Type, TypeVar, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar('T')

class PaginationInfo(BaseModel):
    count: int = Field(description="Number of items in current page")
    total_count: int = Field(description="Total number of items across all pages")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Maximum items per page")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "count": 10,
                "total_count": 100,
                "page": 1,
                "limit": 10
            }
        }
    )

class ApiResponse(BaseModel, Generic[T]):
    message: str
    data: Optional[T] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Operation completed successfully",
                "data": {}
            }
        }
    )

class ApiListResponse(BaseModel, Generic[T]):
    message: str
    data: List[T]
    page: PaginationInfo

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Items retrieved successfully",
                "data": [{}],
                "page": {
                    "count": 1,
                    "total_count": 100,
                    "page": 1,
                    "limit": 10
                }
            }
        }
    )

class ApiCreateResponse(BaseModel, Generic[T]):
    message: str
    id: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Item created successfully",
                "id": "ABC12345"
            }
        }
    )

class ApiUpdateResponse(BaseModel, Generic[T]):
    message: str
    id: str
    modified_at: str

    @field_validator('modified_at', mode='before')
    @classmethod
    def convert_datetime_to_string(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Item updated successfully",
                "id": "ABC12345",
                "modified_at": "2023-10-01T12:00:00Z"
            }
        }
    )

class BaseListResponse(BaseModel, Generic[T]):
    data: List[T]
    total_count: int
    page: int
    limit: int

    @classmethod
    def from_repository_result(
        cls: Type["BaseListResponse[T]"],
        repo_result: Dict[str, Any],
        page: int,
        limit: int,
        record_model: Type[T]
    ) -> "BaseListResponse[T]":
        records = [record_model(**item) for item in repo_result["data"]]
        return cls(
            data=records,
            total_count=repo_result["total_count"],
            page=page,
            limit=limit
        )
    
class BaseSingleUpdateResponse(BaseModel, Generic[T]):
    message: str
    id: str
    modified_at: str

    @field_validator('modified_at', mode='before')
    @classmethod
    def convert_datetime_to_string(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Item updated successfully",
                "id": "ABC12345",
                "modified_at": "2023-10-01T12:00:00Z"
            }
        }
    )
