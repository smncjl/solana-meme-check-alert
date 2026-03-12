from sqlalchemy.orm import Session

from app.repos.evaluations import EvaluationRepo
from app.repos.holders import HolderRepo
from app.repos.pairs import PairRepo
from app.repos.security import SecurityRepo
from app.repos.tokens import TokenRepo
from app.scoring.engine import ScoringEngine, ScoringInput


class EvaluationService:
    def __init__(self, db: Session, scoring_engine: ScoringEngine) -> None:
        self.db = db
        self.engine = scoring_engine
        self.token_repo = TokenRepo(db)
        self.pair_repo = PairRepo(db)
        self.security_repo = SecurityRepo(db)
        self.holder_repo = HolderRepo(db)
        self.eval_repo = EvaluationRepo(db)

    def evaluate_latest_tokens(self, limit: int = 100) -> dict:
        stats = {"tokens_evaluated": 0}
        tokens = self.token_repo.list_latest(limit=limit)
        for token in tokens:
            pair = self.pair_repo.latest_for_token(token.id)
            security = self.security_repo.latest_for_token(token.id)
            holders = self.holder_repo.latest_for_token(token.id)
            if pair is None:
                continue
            scoring_input = ScoringInput(
                liquidity_usd=pair.liquidity_usd,
                volume_5m_usd=pair.volume_5m_usd,
                buys_5m=pair.buys_5m,
                sells_5m=pair.sells_5m,
                holder_count=holders.holder_count if holders else None,
                top10_holder_percent=(
                    security.top10_holder_percent
                    if security and security.top10_holder_percent is not None
                    else (holders.top10_holder_percent if holders else None)
                ),
                creator_holder_percent=security.creator_holder_percent if security else None,
                mint_authority_renounced=security.mint_authority_renounced if security else None,
                freeze_authority_renounced=security.freeze_authority_renounced if security else None,
            )
            result = self.engine.evaluate(scoring_input)
            self.eval_repo.create(
                token_id=token.id,
                risk_score=result.risk_score,
                watch_score=result.watch_score,
                decision=result.decision,
                reasons=result.reasons,
            )
            stats["tokens_evaluated"] += 1

        self.db.commit()
        return stats
