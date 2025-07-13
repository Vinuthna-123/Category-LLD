from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from category.models.base import Base

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:tiger@localhost:5432/mydb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
