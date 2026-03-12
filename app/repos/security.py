from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.token_security import TokenSecurity


class SecurityRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_snapshot(
        self,
        token_id: int,
        mint_authority_renounced: bool | None,
        freeze_authority_renounced: bool | None,
        top10_holder_percent: float | None,
        creator_holder_percent: float | None,
        mutable_metadata: bool | None,
        raw_payload_json: dict,
    ) -> TokenSecurity:
        snapshot = TokenSecurity(
            token_id=token_id,
            mint_authority_renounced=mint_authority_renounced,
            freeze_authority_renounced=freeze_authority_renounced,
            top10_holder_percent=top10_holder_percent,
            creator_holder_percent=creator_holder_percent,
            mutable_metadata=mutable_metadata,
            raw_payload_json=raw_payload_json,
            fetched_at=datetime.utcnow(),
        )
        self.db.add(snapshot)
        self.db.flush()
        return snapshot

    def latest_for_token(self, token_id: int) -> TokenSecurity | None:
        stmt = (
            select(TokenSecurity)
            .where(TokenSecurity.token_id == token_id)
            .order_by(TokenSecurity.fetched_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)
