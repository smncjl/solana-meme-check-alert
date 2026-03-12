from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.token import Token
from app.repos.alerts import AlertRepo
from app.schemas.alert import AlertOut

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(db_session),
) -> list[AlertOut]:
    repo = AlertRepo(db)
    alerts = repo.list_latest(limit)
    out: list[AlertOut] = []
    for alert in alerts:
        token = db.get(Token, alert.token_id)
        out.append(
            AlertOut(
                token_address=token.token_address if token else "unknown",
                channel=alert.channel,
                alert_type=alert.alert_type,
                status=alert.status,
                sent_at=alert.sent_at,
                payload=alert.payload_json,
            )
        )
    return out
