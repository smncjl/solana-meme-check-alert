import pytest

from app.core.config import Settings
from app.repos.alerts import AlertRepo
from app.services.alert_service import AlertService


class FakeTelegram:
    def __init__(self):
        self.messages = []

    async def send_message(self, text: str) -> bool:
        self.messages.append(text)
        return True


@pytest.mark.asyncio
async def test_send_alerts_avoids_duplicates(db, seeded_token):
    settings = Settings(
        APP_ENV="test",
        DATABASE_URL="sqlite:///./test.db",
        MIN_WATCH_SCORE=50,
        MAX_RISK_SCORE_FOR_ALERT=35,
    )
    telegram = FakeTelegram()
    service = AlertService(db, telegram, settings)

    stats_first = await service.send_watch_alerts(limit=50)
    stats_second = await service.send_watch_alerts(limit=50)

    repo = AlertRepo(db)
    alerts = repo.list_latest(10)

    assert stats_first["alerts_sent"] == 1
    assert stats_second["alerts_sent"] == 0
    assert len(alerts) == 1
