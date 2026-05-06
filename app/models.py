from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class URLMap(Base):
    __tablename__ = "url_map"

    code: Mapped[str] = mapped_column(String(5), primary_key=True, index=True)
    long_url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True, index=True)


class CodePool(Base):
    __tablename__ = "code_pool"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(5), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="available", index=True)
    reserved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
