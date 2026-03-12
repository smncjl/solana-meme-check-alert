from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.holder_snapshot import HolderSnapshot


class HolderRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_snapshot(
        self,
        token_id: int,
        holder_count: int | None,
        top10_holder_percent: float | None,
        top20_holder_percent: float | None,
        raw_payload_json: dict,
    ) -> HolderSnapshot:
        snapshot = HolderSnapshot(
            token_id=token_id,
            holder_count=holder_count,
            top10_holder_percent=top10_holder_percent,
            top20_holder_percent=top20_holder_percent,
            raw_payload_json=raw_payload_json,
            fetched_at=datetime.utcnow(),
        )
        self.db.add(snapshot)
        self.db.flush()
        return snapshot

    def latest_for_token(self, token_id: int) -> HolderSnapshot | None:
        stmt = (
            select(HolderSnapshot)
            .where(HolderSnapshot.token_id == token_id)
            .order_by(HolderSnapshot.fetched_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)
