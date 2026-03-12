from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TokenSecurity(Base):
    __tablename__ = "token_security"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token_id: Mapped[int] = mapped_column(ForeignKey("tokens.id", ondelete="CASCADE"), index=True)
    mint_authority_renounced: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    freeze_authority_renounced: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    top10_holder_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    creator_holder_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    mutable_metadata: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    raw_payload_json: Mapped[dict] = mapped_column(JSON)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    token = relationship("Token", back_populates="security_snapshots")
