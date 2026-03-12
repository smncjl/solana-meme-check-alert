from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RiskEvaluation(Base):
    __tablename__ = "risk_evaluations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token_id: Mapped[int] = mapped_column(ForeignKey("tokens.id", ondelete="CASCADE"), index=True)
    risk_score: Mapped[int] = mapped_column(Integer)
    watch_score: Mapped[int] = mapped_column(Integer)
    decision: Mapped[str] = mapped_column(String(32), index=True)
    reasons_json: Mapped[list[str]] = mapped_column(JSON)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    token = relationship("Token", back_populates="evaluations")
