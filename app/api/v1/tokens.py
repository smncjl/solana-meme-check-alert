from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.repos.evaluations import EvaluationRepo
from app.repos.holders import HolderRepo
from app.repos.pairs import PairRepo
from app.repos.security import SecurityRepo
from app.repos.tokens import TokenRepo
from app.schemas.token import (
    HolderSnapshotOut,
    PairSnapshotOut,
    RiskEvaluationOut,
    SecuritySnapshotOut,
    TokenDetailResponse,
    TokenListItem,
)
from app.scoring.decision import recommended_action_for_decision

router = APIRouter(prefix="/api/v1/tokens", tags=["tokens"])


@router.get("", response_model=list[TokenListItem])
def list_tokens(
    limit: int = Query(default=50, ge=1, le=200),
    decision: str | None = Query(default=None),
    db: Session = Depends(db_session),
) -> list[TokenListItem]:
    token_repo = TokenRepo(db)
    eval_repo = EvaluationRepo(db)
    tokens = token_repo.list_latest(limit=limit, decision=decision)
    out: list[TokenListItem] = []
    for token in tokens:
        latest_eval = eval_repo.latest_for_token(token.id)
        out.append(
            TokenListItem(
                token_address=token.token_address,
                symbol=token.symbol,
                name=token.name,
                chain=token.chain,
                first_seen_at=token.first_seen_at,
                decision=latest_eval.decision if latest_eval else None,
                recommended_action=recommended_action_for_decision(
                    latest_eval.decision if latest_eval else None
                ),
                risk_score=latest_eval.risk_score if latest_eval else None,
                watch_score=latest_eval.watch_score if latest_eval else None,
            )
        )
    return out


@router.get("/{token_address}", response_model=TokenDetailResponse)
def get_token_detail(token_address: str, db: Session = Depends(db_session)) -> TokenDetailResponse:
    token_repo = TokenRepo(db)
    pair_repo = PairRepo(db)
    security_repo = SecurityRepo(db)
    holder_repo = HolderRepo(db)
    eval_repo = EvaluationRepo(db)

    token = token_repo.get_by_address(token_address)
    if token is None:
        raise HTTPException(status_code=404, detail="token not found")

    pair = pair_repo.latest_for_token(token.id)
    security = security_repo.latest_for_token(token.id)
    holders = holder_repo.latest_for_token(token.id)
    evaluation = eval_repo.latest_for_token(token.id)

    return TokenDetailResponse(
        token_address=token.token_address,
        symbol=token.symbol,
        name=token.name,
        chain=token.chain,
        first_seen_at=token.first_seen_at,
        latest_pair=(
            PairSnapshotOut(
                dex_name=pair.dex_name,
                pair_address=pair.pair_address,
                quote_token=pair.quote_token,
                liquidity_usd=pair.liquidity_usd,
                fdv_usd=pair.fdv_usd,
                market_cap_usd=pair.market_cap_usd,
                price_usd=pair.price_usd,
                volume_5m_usd=pair.volume_5m_usd,
                volume_1h_usd=pair.volume_1h_usd,
                buys_5m=pair.buys_5m,
                sells_5m=pair.sells_5m,
                snapshot_at=pair.snapshot_at,
            )
            if pair
            else None
        ),
        latest_security=(
            SecuritySnapshotOut(
                mint_authority_renounced=security.mint_authority_renounced,
                freeze_authority_renounced=security.freeze_authority_renounced,
                top10_holder_percent=security.top10_holder_percent,
                creator_holder_percent=security.creator_holder_percent,
                mutable_metadata=security.mutable_metadata,
                fetched_at=security.fetched_at,
            )
            if security
            else None
        ),
        latest_holders=(
            HolderSnapshotOut(
                holder_count=holders.holder_count,
                top10_holder_percent=holders.top10_holder_percent,
                top20_holder_percent=holders.top20_holder_percent,
                fetched_at=holders.fetched_at,
            )
            if holders
            else None
        ),
        latest_evaluation=(
            RiskEvaluationOut(
                risk_score=evaluation.risk_score,
                watch_score=evaluation.watch_score,
                decision=evaluation.decision,
                recommended_action=recommended_action_for_decision(evaluation.decision),
                reasons=evaluation.reasons_json,
                evaluated_at=evaluation.evaluated_at,
            )
            if evaluation
            else None
        ),
    )
