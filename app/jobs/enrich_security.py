import logging

from app.clients.birdeye import BirdeyeClient
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.enrichment_service import EnrichmentService

logger = logging.getLogger(__name__)


async def run_enrich_security_job() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        service = EnrichmentService(
            db,
            BirdeyeClient(settings.birdeye_base_url, settings.birdeye_api_key),
        )
        stats = await service.enrich_recent_tokens(limit=75)
        logger.info("enrich_security_completed stats=%s", stats)
    finally:
        db.close()
