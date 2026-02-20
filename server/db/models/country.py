from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from db.base import Base


class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    official_name = Column(String, nullable=True)
    wiki = Column(String, nullable=True)
    md_file = Column(String, nullable=False)
