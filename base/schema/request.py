from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal

class Pagination(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=10, ge=1, le=1000, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

class SortBy(BaseModel):
    field: str = Field(..., description="Field to sort by")
    order: Literal["asc", "desc"] = Field(default="desc", description="Sort order")

class DateRange(BaseModel):
    from_: Optional[str] = Field(alias="from")
    to: Optional[str] = Field(default=None,description="End date for filtering (inclusive)")

class CreatedAt(DateRange):
    pass

class ModifiedAt(DateRange):
    pass

class FilterExpression(BaseModel):
    op: Literal["eq", "ne", "gt", "lt", "gte", "lte", "in", "nin", "between"]
    value: Union[str, int, List[Union[str, int]]]

class Search(BaseModel):
    field: str = Field(default="name", description="Field to search in")
    value: str = Field(default="", description="Search value")

class BaseFilters(BaseModel):
    pass

class BaseListRequest(BaseModel):
    filters: Optional[BaseFilters] = None
    search: Optional[Search] = None
    pagination: Optional[Pagination] = Pagination()
    sort_by: Optional[List[SortBy]] = [SortBy(field="created_at", order="desc")]
    include_deleted: Optional[bool] = Field(default=False)
