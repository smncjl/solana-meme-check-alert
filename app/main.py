import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.scheduler import scheduler
from app.jobs.discover_pairs import run_discover_pairs_job
from app.jobs.enrich_security import run_enrich_security_job
from app.jobs.evaluate_tokens import run_evaluate_tokens_job
from app.jobs.send_alerts import run_send_alerts_job

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.scheduler_enabled:
        _configure_scheduler()
        scheduler.start()
        logger.info("scheduler_started")
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)


app = FastAPI(title="solana-rug-guard", lifespan=lifespan)
app.include_router(api_router)


def _configure_scheduler() -> None:
    if settings.discovery_enabled:
        scheduler.add_job(
            lambda: asyncio.run(run_discover_pairs_job()),
            "interval",
            seconds=settings.discovery_interval_seconds,
            id="discover_pairs",
            replace_existing=True,
        )

    if settings.enrichment_enabled:
        scheduler.add_job(
            lambda: asyncio.run(run_enrich_security_job()),
            "interval",
            seconds=settings.enrichment_interval_seconds,
            id="enrich_security",
            replace_existing=True,
        )

    scheduler.add_job(
        run_evaluate_tokens_job,
        "interval",
        seconds=settings.evaluation_interval_seconds,
        id="evaluate_tokens",
        replace_existing=True,
    )

    if settings.alerting_enabled:
        scheduler.add_job(
            lambda: asyncio.run(run_send_alerts_job()),
            "interval",
            seconds=settings.alert_interval_seconds,
            id="send_alerts",
            replace_existing=True,
        )
