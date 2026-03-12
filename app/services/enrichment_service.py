import logging

from sqlalchemy.orm import Session

from app.clients.birdeye import BirdeyeClient
from app.repos.holders import HolderRepo
from app.repos.security import SecurityRepo
from app.repos.tokens import TokenRepo

logger = logging.getLogger(__name__)


class EnrichmentService:
    def __init__(self, db: Session, birdeye_client: BirdeyeClient) -> None:
        self.db = db
        self.birdeye_client = birdeye_client
        self.token_repo = TokenRepo(db)
        self.security_repo = SecurityRepo(db)
        self.holder_repo = HolderRepo(db)

    async def enrich_recent_tokens(self, limit: int = 50) -> dict:
        stats = {"tokens_checked": 0, "security_saved": 0, "holders_saved": 0}
        tokens = self.token_repo.recent_without_security(limit=limit)
        for token in tokens:
            stats["tokens_checked"] += 1
            security = await self.birdeye_client.fetch_security(token.token_address)
            if security:
                self.security_repo.create_snapshot(
                    token_id=token.id,
                    mint_authority_renounced=security.mint_authority_renounced,
                    freeze_authority_renounced=security.freeze_authority_renounced,
                    top10_holder_percent=security.top10_holder_percent,
                    creator_holder_percent=security.creator_holder_percent,
                    mutable_metadata=security.mutable_metadata,
                    raw_payload_json=security.raw_payload_json,
                )
                stats["security_saved"] += 1

            holders = await self.birdeye_client.fetch_holders(token.token_address)
            if holders:
                self.holder_repo.create_snapshot(
                    token_id=token.id,
                    holder_count=holders.holder_count,
                    top10_holder_percent=holders.top10_holder_percent,
                    top20_holder_percent=holders.top20_holder_percent,
                    raw_payload_json=holders.raw_payload_json,
                )
                stats["holders_saved"] += 1

        self.db.commit()
        return stats
