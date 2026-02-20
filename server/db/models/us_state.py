from sqlalchemy import (
    Column,
    Integer,
    String,
)
from db.base import Base


class USState(Base):
    __tablename__ = "us_states"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=True)
