from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Category(Base, TimestampMixin):
    __tablename__ = "categories"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    