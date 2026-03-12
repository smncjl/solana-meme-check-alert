from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alert import Alert


class AlertRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def has_existing_alert(self, token_id: int, alert_type: str) -> bool:
        stmt = (
            select(Alert.id)
            .where(Alert.token_id == token_id)
            .where(Alert.alert_type == alert_type)
            .limit(1)
        )
        return self.db.scalar(stmt) is not None

    def create(
        self,
        token_id: int,
        channel: str,
        alert_type: str,
        payload_json: dict,
        status: str,
    ) -> Alert:
        alert = Alert(
            token_id=token_id,
            channel=channel,
            alert_type=alert_type,
            payload_json=payload_json,
            sent_at=datetime.utcnow(),
            status=status,
        )
        self.db.add(alert)
        self.db.flush()
        return alert

    def list_latest(self, limit: int) -> list[Alert]:
        stmt = select(Alert).order_by(Alert.sent_at.desc()).limit(limit)
        return list(self.db.scalars(stmt).all())
