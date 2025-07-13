from typing import Optional, List, Dict, Any
from base.repository.base_repo import BaseRepository
from category.models.category import Category

class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db):
        super().__init__(db)
        self.model = Category