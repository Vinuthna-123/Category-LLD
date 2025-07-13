import logging
from typing import Dict, Any, Optional
from base.services.base_service import BaseService
from category.models.category import Category
from sqlalchemy.orm import Session
from fastapi import HTTPException
from category.repository.category import CategoryRepository
from category.schema.category import (CategoryListRequest,CategoryListResponse,CreateCategoryRequest,CreateCategoryResponse,UpdateCategoryRequest,GetCategoryResponse,UpdateCategoryResponse,CategoryRecord)

logger = logging.getLogger(__name__)

class CategoryService(BaseService):
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.repository = self._get_repository()

    def _get_repository(self) -> CategoryRepository:
        return CategoryRepository(self.db)
    
    def list_categories(self, request: CategoryListRequest) -> CategoryListResponse:
        repo_result = self.list(
        model_class=Category,
        pagination=request.pagination,
        sort_by=request.sort_by,
        filters=request.filters,
        include_deleted=request.include_deleted
        )
        return CategoryListResponse.from_repository_result(
        repo_result=repo_result,
        page=request.pagination.page,
        limit=request.pagination.limit,
        record_model=CategoryRecord
        )
    def create_category(self, request: CreateCategoryRequest) -> CreateCategoryResponse:
        created_id = self.create_one(model_class=Category, pydantic_obj=request)
        return CreateCategoryResponse(id=created_id)
    
    def get_category_by_id(self, category_id: str) -> GetCategoryResponse:
        category_obj = self.repository.get_by_id(Category, category_id)
        if not category_obj:
            raise HTTPException(status_code=404, detail="Category not found")
        category_data = CategoryRecord.model_validate(category_obj)
        return GetCategoryResponse(data=category_data)

    def update_category(self, category_id: str, request: UpdateCategoryRequest) -> UpdateCategoryResponse:
        existing = self.get_by_id(Category, category_id)
        if not existing:
            raise ValueError(f"Category with ID {category_id} not found.")

        updated = self.repository.update_one_by_id(model=Category,record_id=category_id,fields_to_update=request.model_dump(exclude_unset=True))
        return UpdateCategoryResponse(message="Category updated successfully",id=category_id,modified_at=updated["updated_at"])

    def delete_category(self, category_id: str) -> int:
        return self.delete_by_id(Category, category_id)

