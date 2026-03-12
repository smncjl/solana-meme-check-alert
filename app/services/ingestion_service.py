import logging

from sqlalchemy.orm import Session

from app.clients.dexscreener import DexscreenerClient
from app.repos.ingestion_runs import IngestionRunRepo
from app.repos.pairs import PairRepo
from app.repos.tokens import TokenRepo

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, db: Session, dexscreener_client: DexscreenerClient) -> None:
        self.db = db
        self.dexscreener_client = dexscreener_client
        self.token_repo = TokenRepo(db)
        self.pair_repo = PairRepo(db)
        self.run_repo = IngestionRunRepo(db)

    async def discover_pairs(self) -> dict:
        run = self.run_repo.start(source="dexscreener")
        stats = {"pairs_seen": 0, "tokens_upserted": 0, "snapshots_saved": 0}
        try:
            pairs = await self.dexscreener_client.fetch_latest_solana_pairs()
            stats["pairs_seen"] = len(pairs)
            for pair in pairs:
                token = self.token_repo.upsert_token(
                    chain=pair.chain,
                    token_address=pair.token_address,
                    symbol=pair.symbol,
                    name=pair.name,
                )
                stats["tokens_upserted"] += 1
                self.pair_repo.add_snapshot(
                    token_id=token.id,
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
                    pair_created_at=pair.pair_created_at,
                )
                stats["snapshots_saved"] += 1

            self.run_repo.finish(run, status="success", stats_json=stats)
            self.db.commit()
            return stats
        except Exception:
            self.db.rollback()
            logger.exception("discover_pairs_failed")
            return stats
