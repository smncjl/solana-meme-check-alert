from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chain: Mapped[str] = mapped_column(String(32), index=True)
    token_address: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    symbol: Mapped[str] = mapped_column(String(64), default="")
    name: Mapped[str] = mapped_column(String(255), default="")
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    pairs = relationship("Pair", back_populates="token")
    security_snapshots = relationship("TokenSecurity", back_populates="token")
    holder_snapshots = relationship("HolderSnapshot", back_populates="token")
    evaluations = relationship("RiskEvaluation", back_populates="token")
    alerts = relationship("Alert", back_populates="token")


Index("ix_tokens_chain_first_seen", Token.chain, Token.first_seen_at)
