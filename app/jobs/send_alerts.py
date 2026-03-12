import logging

from app.clients.telegram import TelegramClient
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)


async def run_send_alerts_job() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        service = AlertService(
            db,
            TelegramClient(settings.telegram_bot_token, settings.telegram_chat_id),
            settings,
        )
        stats = await service.send_watch_alerts(limit=100)
        logger.info("send_alerts_completed stats=%s", stats)
    finally:
        db.close()
