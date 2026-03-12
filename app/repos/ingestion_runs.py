from datetime import datetime

from sqlalchemy.orm import Session

from app.models.ingestion_run import IngestionRun


class IngestionRunRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def start(self, source: str) -> IngestionRun:
        run = IngestionRun(source=source, started_at=datetime.utcnow(), status="running", stats_json={})
        self.db.add(run)
        self.db.flush()
        return run

    def finish(self, run: IngestionRun, status: str, stats_json: dict) -> IngestionRun:
        run.finished_at = datetime.utcnow()
        run.status = status
        run.stats_json = stats_json
        self.db.flush()
        return run
