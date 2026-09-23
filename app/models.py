"""Modèles SQLAlchemy pour la traçabilité des interactions de l'agent."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    instruction: Mapped[str] = mapped_column(Text)
    response: Mapped[str] = mapped_column(Text)
    generation_time_ms: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    method: Mapped[str] = mapped_column(Text)
    path: Mapped[str] = mapped_column(Text)
    status_code: Mapped[int] = mapped_column(Integer)
    total_time_ms: Mapped[float] = mapped_column(Float)
    interaction_id: Mapped[int | None] = mapped_column(ForeignKey("interactions.id"))
    error_detail: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
