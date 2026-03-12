from pydantic import BaseModel


class ScoringRules(BaseModel):
    risk_liquidity_low_threshold: float = 25_000
    risk_liquidity_mid_threshold: float = 60_000
    risk_top10_high_threshold: float = 35
    risk_top10_mid_threshold: float = 25
    risk_creator_holder_threshold: float = 10
    risk_holders_low_threshold: int = 150

    watch_liquidity_threshold: float = 50_000
    watch_volume_5m_threshold: float = 20_000
    watch_holders_threshold: int = 300
    watch_top10_good_threshold: float = 25

    reject_risk_threshold: int = 70
    caution_risk_threshold: int = 40
    watch_min_watch_score: int = 50
    alert_risk_threshold: int = 30
    alert_watch_threshold: int = 70
