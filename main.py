from fastapi import FastAPI
from core.database import init_db
from category.api.v1.category import category_router

app = FastAPI()


init_db()
app.include_router(category_router, prefix="/categories", tags=["Categories"])
