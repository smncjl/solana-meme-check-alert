from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.alert import Alert
from app.models.risk_evaluation import RiskEvaluation
from app.models.token import Token
from app.schemas.stats import SummaryStatsResponse

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get("/summary", response_model=SummaryStatsResponse)
def summary(db: Session = Depends(db_session)) -> SummaryStatsResponse:
    tokens_tracked = db.scalar(select(func.count(Token.id))) or 0
    evaluations_total = db.scalar(select(func.count(RiskEvaluation.id))) or 0
    alerts_total = db.scalar(select(func.count(Alert.id))) or 0

    decision_rows = db.execute(
        select(RiskEvaluation.decision, func.count(RiskEvaluation.id))
        .group_by(RiskEvaluation.decision)
        .order_by(func.count(RiskEvaluation.id).desc())
    ).all()

    return SummaryStatsResponse(
        tokens_tracked=int(tokens_tracked),
        evaluations_total=int(evaluations_total),
        alerts_total=int(alerts_total),
        latest_decision_counts={row[0]: int(row[1]) for row in decision_rows},
    )
