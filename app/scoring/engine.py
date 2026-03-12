from dataclasses import dataclass

from app.scoring.rules import ScoringRules


@dataclass
class ScoringInput:
    liquidity_usd: float | None = None
    volume_5m_usd: float | None = None
    buys_5m: int | None = None
    sells_5m: int | None = None
    holder_count: int | None = None
    top10_holder_percent: float | None = None
    creator_holder_percent: float | None = None
    mint_authority_renounced: bool | None = None
    freeze_authority_renounced: bool | None = None


@dataclass
class ScoringResult:
    risk_score: int
    watch_score: int
    decision: str
    reasons: list[str]


class ScoringEngine:
    def __init__(self, rules: ScoringRules | None = None) -> None:
        self.rules = rules or ScoringRules()

    def evaluate(self, data: ScoringInput) -> ScoringResult:
        risk_score = 0
        watch_score = 0
        reasons: list[str] = []

        liquidity = data.liquidity_usd
        if liquidity is None:
            risk_score += 10
            reasons.append("missing_liquidity_data")
        elif liquidity < self.rules.risk_liquidity_low_threshold:
            risk_score += 25
            reasons.append("low_liquidity")
        elif liquidity < self.rules.risk_liquidity_mid_threshold:
            risk_score += 10
            reasons.append("moderate_liquidity")

        top10 = data.top10_holder_percent
        if top10 is None:
            risk_score += 10
            reasons.append("missing_top10_concentration")
        elif top10 > self.rules.risk_top10_high_threshold:
            risk_score += 25
            reasons.append("high_holder_concentration")
        elif top10 > self.rules.risk_top10_mid_threshold:
            risk_score += 10
            reasons.append("moderate_holder_concentration")

        creator = data.creator_holder_percent
        if creator is not None and creator > self.rules.risk_creator_holder_threshold:
            risk_score += 20
            reasons.append("creator_holds_large_share")

        if data.mint_authority_renounced is False:
            risk_score += 15
            reasons.append("mint_authority_not_renounced")
        if data.freeze_authority_renounced is False:
            risk_score += 15
            reasons.append("freeze_authority_not_renounced")

        holders = data.holder_count
        if holders is None:
            risk_score += 10
            reasons.append("missing_holder_count")
        elif holders < self.rules.risk_holders_low_threshold:
            risk_score += 10
            reasons.append("low_holder_count")

        volume = data.volume_5m_usd
        if liquidity and volume and liquidity > 0 and volume / liquidity > 4.0:
            risk_score += 10
            reasons.append("abnormal_volume_liquidity_ratio")

        risk_score = min(100, max(0, risk_score))

        if liquidity is not None and liquidity >= self.rules.watch_liquidity_threshold:
            watch_score += 20
        if volume is not None and volume >= self.rules.watch_volume_5m_threshold:
            watch_score += 20
        if data.buys_5m is not None and data.sells_5m is not None and data.buys_5m > data.sells_5m:
            watch_score += 10
        if holders is not None and holders >= self.rules.watch_holders_threshold:
            watch_score += 15
        if top10 is not None and top10 <= self.rules.watch_top10_good_threshold:
            watch_score += 15
        if risk_score <= 35:
            watch_score += 20

        watch_score = min(100, max(0, watch_score))

        if risk_score >= self.rules.reject_risk_threshold:
            decision = "REJECT"
        elif risk_score >= self.rules.caution_risk_threshold:
            decision = "CAUTION"
        elif risk_score < self.rules.alert_risk_threshold and watch_score >= self.rules.alert_watch_threshold:
            decision = "ALERT"
        elif watch_score >= self.rules.watch_min_watch_score:
            decision = "WATCH"
        else:
            decision = "CAUTION"

        return ScoringResult(
            risk_score=risk_score,
            watch_score=watch_score,
            decision=decision,
            reasons=reasons,
        )
