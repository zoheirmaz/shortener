from sqlalchemy import Column, Integer, String

from .database import Base


class URLMapping(Base):
    __tablename__ = "url_mappings"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String(2048), unique=True, nullable=False, index=True)
    short_code = Column(String(5), unique=True, nullable=False, index=True)
