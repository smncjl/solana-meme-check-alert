from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class HolderSnapshot(Base):
    __tablename__ = "holder_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token_id: Mapped[int] = mapped_column(ForeignKey("tokens.id", ondelete="CASCADE"), index=True)
    holder_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    top10_holder_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    top20_holder_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_payload_json: Mapped[dict] = mapped_column(JSON)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    token = relationship("Token", back_populates="holder_snapshots")
