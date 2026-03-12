import logging

from app.clients.dexscreener import DexscreenerClient
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.ingestion_service import IngestionService

logger = logging.getLogger(__name__)


async def run_discover_pairs_job() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        service = IngestionService(db, DexscreenerClient(settings.dexscreener_base_url))
        stats = await service.discover_pairs()
        logger.info("discover_pairs_completed stats=%s", stats)
    finally:
        db.close()
