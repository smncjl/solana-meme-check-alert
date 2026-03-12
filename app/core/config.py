from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="dev", alias="APP_ENV")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/solana_rug_guard",
        alias="DATABASE_URL",
    )

    dexscreener_base_url: str = Field(default="https://api.dexscreener.com", alias="DEXSCREENER_BASE_URL")
    birdeye_base_url: str = Field(default="https://public-api.birdeye.so", alias="BIRDEYE_BASE_URL")
    birdeye_api_key: str = Field(default="", alias="BIRDEYE_API_KEY")

    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", alias="TELEGRAM_CHAT_ID")

    discovery_enabled: bool = Field(default=True, alias="DISCOVERY_ENABLED")
    enrichment_enabled: bool = Field(default=True, alias="ENRICHMENT_ENABLED")
    alerting_enabled: bool = Field(default=True, alias="ALERTING_ENABLED")
    scheduler_enabled: bool = Field(default=True, alias="SCHEDULER_ENABLED")

    min_watch_score: int = Field(default=50, alias="MIN_WATCH_SCORE")
    max_risk_score_for_alert: int = Field(default=35, alias="MAX_RISK_SCORE_FOR_ALERT")

    discovery_interval_seconds: int = Field(default=60, alias="DISCOVERY_INTERVAL_SECONDS")
    enrichment_interval_seconds: int = Field(default=120, alias="ENRICHMENT_INTERVAL_SECONDS")
    evaluation_interval_seconds: int = Field(default=120, alias="EVALUATION_INTERVAL_SECONDS")
    alert_interval_seconds: int = Field(default=60, alias="ALERT_INTERVAL_SECONDS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
