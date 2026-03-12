import logging

from app.core.database import SessionLocal
from app.scoring.engine import ScoringEngine
from app.services.evaluation_service import EvaluationService

logger = logging.getLogger(__name__)


def run_evaluate_tokens_job() -> None:
    db = SessionLocal()
    try:
        service = EvaluationService(db, ScoringEngine())
        stats = service.evaluate_latest_tokens(limit=100)
        logger.info("evaluate_tokens_completed stats=%s", stats)
    finally:
        db.close()
