from fastapi import APIRouter, Depends, HTTPException
import logging
from category.service.category import CategoryService
from category.schema.category import (CategoryListRequest,CategoryListResponse,CreateCategoryRequest,CreateCategoryResponse,UpdateCategoryRequest,UpdateCategoryResponse,GetCategoryResponse)
from base.schema.response import (ApiCreateResponse,ApiUpdateResponse)
from sqlalchemy.orm import Session
from core.database import get_db

logger = logging.getLogger(__name__)

category_router = APIRouter(prefix="/api/v1", tags=["Categories"])

# Dependency for service
def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


@category_router.post("/list", response_model=CategoryListResponse)
async def list_categories(request: CategoryListRequest,service: CategoryService = Depends(get_category_service)) -> CategoryListResponse:
    try:
        return service.list_categories(request)
    except Exception as e:
        logger.error(f"Error in list_categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@category_router.post("/", response_model=ApiCreateResponse[CreateCategoryResponse])
async def create_category(request: CreateCategoryRequest,service: CategoryService = Depends(get_category_service)) -> ApiCreateResponse:
    try:
        result = service.create_category(request)
        return ApiCreateResponse(message="Category created successfully", id=result.id)
    except Exception as e:
        logger.error(f"Error in create_category: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@category_router.put("/{category_id}", response_model=UpdateCategoryResponse)
async def update_category(category_id: str,request: UpdateCategoryRequest,service: CategoryService = Depends(get_category_service)) -> UpdateCategoryResponse:
    try:
        return service.update_category(category_id, request)
    except Exception as e:
        logger.error(f"Error in update_category: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@category_router.get("/{category_id}", response_model=GetCategoryResponse)
async def get_category(category_id: str,service: CategoryService = Depends(get_category_service)) -> GetCategoryResponse:
    try:
        result = service.get_by_id(service.repository.model, category_id)
        if not result:
            raise HTTPException(status_code=404, detail="Category not found")
        return GetCategoryResponse(data=result)
    except Exception as e:
        logger.error(f"Error in get_category: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@category_router.delete("/{category_id}", response_model=ApiUpdateResponse)
async def delete_category(category_id: str,service: CategoryService = Depends(get_category_service)) -> ApiUpdateResponse:
    try:
        deleted = service.delete_category(category_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Category not found")
        return ApiUpdateResponse(message="Category deleted successfully", id=category_id)
    except Exception as e:
        logger.error(f"Error in delete_category: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
