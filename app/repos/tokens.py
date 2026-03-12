from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.risk_evaluation import RiskEvaluation
from app.models.token import Token


class TokenRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_address(self, token_address: str) -> Token | None:
        return self.db.scalar(select(Token).where(Token.token_address == token_address))

    def get_by_id(self, token_id: int) -> Token | None:
        return self.db.get(Token, token_id)

    def upsert_token(self, chain: str, token_address: str, symbol: str, name: str) -> Token:
        token = self.get_by_address(token_address)
        now = datetime.utcnow()
        if token is None:
            token = Token(
                chain=chain,
                token_address=token_address,
                symbol=symbol,
                name=name,
                first_seen_at=now,
                created_at=now,
                updated_at=now,
            )
            self.db.add(token)
            self.db.flush()
            return token

        token.symbol = symbol or token.symbol
        token.name = name or token.name
        token.updated_at = now
        self.db.flush()
        return token

    def list_latest(self, limit: int, decision: str | None = None) -> list[Token]:
        stmt: Select[tuple[Token]] = select(Token).order_by(Token.first_seen_at.desc()).limit(limit)
        if decision:
            latest_eval_subq = (
                select(
                    RiskEvaluation.token_id,
                    func.max(RiskEvaluation.evaluated_at).label("max_evaluated_at"),
                )
                .group_by(RiskEvaluation.token_id)
                .subquery()
            )
            latest_eval = (
                select(RiskEvaluation.token_id, RiskEvaluation.decision)
                .join(
                    latest_eval_subq,
                    (RiskEvaluation.token_id == latest_eval_subq.c.token_id)
                    & (RiskEvaluation.evaluated_at == latest_eval_subq.c.max_evaluated_at),
                )
                .subquery()
            )
            stmt = (
                select(Token)
                .join(latest_eval, latest_eval.c.token_id == Token.id)
                .where(latest_eval.c.decision == decision)
                .order_by(Token.first_seen_at.desc())
                .limit(limit)
            )
        return list(self.db.scalars(stmt).all())

    def recent_without_security(self, limit: int = 50) -> list[Token]:
        from app.models.token_security import TokenSecurity

        stmt = (
            select(Token)
            .outerjoin(TokenSecurity, TokenSecurity.token_id == Token.id)
            .where(TokenSecurity.id.is_(None))
            .order_by(Token.first_seen_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
