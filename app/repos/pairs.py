from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pair import Pair


class PairRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_snapshot(
        self,
        token_id: int,
        dex_name: str,
        pair_address: str,
        quote_token: str,
        liquidity_usd: float | None,
        fdv_usd: float | None,
        market_cap_usd: float | None,
        price_usd: float | None,
        volume_5m_usd: float | None,
        volume_1h_usd: float | None,
        buys_5m: int | None,
        sells_5m: int | None,
        pair_created_at: datetime | None,
    ) -> Pair:
        pair = Pair(
            token_id=token_id,
            dex_name=dex_name,
            pair_address=pair_address,
            quote_token=quote_token,
            liquidity_usd=liquidity_usd,
            fdv_usd=fdv_usd,
            market_cap_usd=market_cap_usd,
            price_usd=price_usd,
            volume_5m_usd=volume_5m_usd,
            volume_1h_usd=volume_1h_usd,
            buys_5m=buys_5m,
            sells_5m=sells_5m,
            pair_created_at=pair_created_at,
            snapshot_at=datetime.utcnow(),
        )
        self.db.add(pair)
        self.db.flush()
        return pair

    def latest_for_token(self, token_id: int) -> Pair | None:
        stmt = select(Pair).where(Pair.token_id == token_id).order_by(Pair.snapshot_at.desc()).limit(1)
        return self.db.scalar(stmt)
