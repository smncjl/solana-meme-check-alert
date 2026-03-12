from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Pair(Base):
    __tablename__ = "pairs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token_id: Mapped[int] = mapped_column(ForeignKey("tokens.id", ondelete="CASCADE"), index=True)
    dex_name: Mapped[str] = mapped_column(String(64))
    pair_address: Mapped[str] = mapped_column(String(64), index=True)
    quote_token: Mapped[str] = mapped_column(String(64), default="")
    liquidity_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    fdv_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    market_cap_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume_5m_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume_1h_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    buys_5m: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sells_5m: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pair_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    token = relationship("Token", back_populates="pairs")
