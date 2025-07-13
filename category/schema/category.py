from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from base.schema.request import (BaseListRequest,BaseFilters,CreatedAt,ModifiedAt,FilterExpression)
from base.schema.response import BaseListResponse, BaseSingleUpdateResponse


class CategoryFilters(BaseFilters):
    name: Optional[FilterExpression]
    created_at: Optional[CreatedAt] = None
    modified_at: Optional[ModifiedAt] = None

class SortByField(BaseModel):
    field: str
    order: Literal["asc", "desc"] = "asc"

class CategoryListRequest(BaseListRequest):
    filters: Optional[CategoryFilters] = None
    sort_by: Optional[List[SortByField]] = None


class CategoryRecord(BaseModel):
    id: str = Field(description="Unique identifier of the category")
    name: str = Field(description="Name of the category")
    description: Optional[str] = Field(default=None, description="Description of the category")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    is_deleted: Optional[bool] = Field(default=False, description="Soft delete flag")

    class Config:
        from_attributes = True

class CategoryListResponse(BaseListResponse):
    data: List[CategoryRecord] = Field(default_factory=list,description="List of category records")

class CreateCategoryRequest(BaseModel):
    name: str = Field(description="Name of the category")
    description: Optional[str] = Field(default=None, description="Description of the category")


class CreateCategoryResponse(BaseModel):
    id: str = Field(description="ID of the created category")

class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = Field(default=None, description="Updated name of the category")
    description: Optional[str] = Field(default=None, description="Updated description of the category")

class UpdateCategoryResponse(BaseSingleUpdateResponse):
    pass

class GetCategoryResponse(BaseModel):
    data: CategoryRecord = Field(description="Details of the category")
