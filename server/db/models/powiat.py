from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from db.base import Base


class Powiat(Base):
    __tablename__ = "powiaty"
    id = Column(Integer, primary_key=True, index=True)
    nazwa = Column(String, nullable=False)
    # We can add more fields later if needed (e.g., voivodeship, population, etc.)
