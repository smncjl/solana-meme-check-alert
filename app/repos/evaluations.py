from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.risk_evaluation import RiskEvaluation


class EvaluationRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        token_id: int,
        risk_score: int,
        watch_score: int,
        decision: str,
        reasons: list[str],
    ) -> RiskEvaluation:
        evaluation = RiskEvaluation(
            token_id=token_id,
            risk_score=risk_score,
            watch_score=watch_score,
            decision=decision,
            reasons_json=reasons,
            evaluated_at=datetime.utcnow(),
        )
        self.db.add(evaluation)
        self.db.flush()
        return evaluation

    def latest_for_token(self, token_id: int) -> RiskEvaluation | None:
        stmt = (
            select(RiskEvaluation)
            .where(RiskEvaluation.token_id == token_id)
            .order_by(RiskEvaluation.evaluated_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def list_latest(self, limit: int = 100) -> list[RiskEvaluation]:
        stmt = select(RiskEvaluation).order_by(RiskEvaluation.evaluated_at.desc()).limit(limit)
        return list(self.db.scalars(stmt).all())
