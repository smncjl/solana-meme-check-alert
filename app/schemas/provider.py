from datetime import datetime

from pydantic import BaseModel


class NormalizedPair(BaseModel):
    chain: str
    token_address: str
    symbol: str
    name: str
    dex_name: str
    pair_address: str
    quote_token: str
    liquidity_usd: float | None = None
    fdv_usd: float | None = None
    market_cap_usd: float | None = None
    price_usd: float | None = None
    volume_5m_usd: float | None = None
    volume_1h_usd: float | None = None
    buys_5m: int | None = None
    sells_5m: int | None = None
    pair_created_at: datetime | None = None


class NormalizedSecurity(BaseModel):
    mint_authority_renounced: bool | None = None
    freeze_authority_renounced: bool | None = None
    top10_holder_percent: float | None = None
    creator_holder_percent: float | None = None
    mutable_metadata: bool | None = None
    raw_payload_json: dict


class NormalizedHolders(BaseModel):
    holder_count: int | None = None
    top10_holder_percent: float | None = None
    top20_holder_percent: float | None = None
    raw_payload_json: dict
