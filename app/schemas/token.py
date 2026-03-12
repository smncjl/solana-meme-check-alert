from datetime import datetime

from pydantic import BaseModel


class TokenListItem(BaseModel):
    token_address: str
    symbol: str
    name: str
    chain: str
    first_seen_at: datetime
    decision: str | None = None
    recommended_action: str
    risk_score: int | None = None
    watch_score: int | None = None


class PairSnapshotOut(BaseModel):
    dex_name: str
    pair_address: str
    quote_token: str
    liquidity_usd: float | None
    fdv_usd: float | None
    market_cap_usd: float | None
    price_usd: float | None
    volume_5m_usd: float | None
    volume_1h_usd: float | None
    buys_5m: int | None
    sells_5m: int | None
    snapshot_at: datetime


class SecuritySnapshotOut(BaseModel):
    mint_authority_renounced: bool | None
    freeze_authority_renounced: bool | None
    top10_holder_percent: float | None
    creator_holder_percent: float | None
    mutable_metadata: bool | None
    fetched_at: datetime


class HolderSnapshotOut(BaseModel):
    holder_count: int | None
    top10_holder_percent: float | None
    top20_holder_percent: float | None
    fetched_at: datetime


class RiskEvaluationOut(BaseModel):
    risk_score: int
    watch_score: int
    decision: str
    recommended_action: str
    reasons: list[str]
    evaluated_at: datetime


class TokenDetailResponse(BaseModel):
    token_address: str
    symbol: str
    name: str
    chain: str
    first_seen_at: datetime
    latest_pair: PairSnapshotOut | None
    latest_security: SecuritySnapshotOut | None
    latest_holders: HolderSnapshotOut | None
    latest_evaluation: RiskEvaluationOut | None
