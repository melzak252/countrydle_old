from sqlalchemy import (
    Column,
    Integer,
    String,
)
from db.base import Base


class Wojewodztwo(Base):
    __tablename__ = "wojewodztwa"
    id = Column(Integer, primary_key=True, index=True)
    nazwa = Column(String, nullable=False)
