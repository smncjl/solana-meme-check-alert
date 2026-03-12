from typing import Protocol

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.repos.alerts import AlertRepo
from app.repos.evaluations import EvaluationRepo
from app.repos.holders import HolderRepo
from app.repos.pairs import PairRepo
from app.repos.tokens import TokenRepo


class TelegramSender(Protocol):
    async def send_message(self, text: str) -> bool: ...


class AlertService:
    def __init__(self, db: Session, telegram_client: TelegramSender, settings: Settings) -> None:
        self.db = db
        self.telegram_client = telegram_client
        self.settings = settings
        self.alert_repo = AlertRepo(db)
        self.eval_repo = EvaluationRepo(db)
        self.token_repo = TokenRepo(db)
        self.pair_repo = PairRepo(db)
        self.holder_repo = HolderRepo(db)

    async def send_watch_alerts(self, limit: int = 100) -> dict:
        stats = {"evaluations_checked": 0, "alerts_sent": 0}
        evaluations = self.eval_repo.list_latest(limit=limit)
        for evaluation in evaluations:
            stats["evaluations_checked"] += 1
            if evaluation.watch_score < self.settings.min_watch_score:
                continue
            if evaluation.risk_score > self.settings.max_risk_score_for_alert:
                continue
            if evaluation.decision not in {"WATCH", "ALERT"}:
                continue
            if self.alert_repo.has_existing_alert(evaluation.token_id, alert_type="watch_signal"):
                continue

            token = self.token_repo.get_by_id(evaluation.token_id)
            pair = self.pair_repo.latest_for_token(evaluation.token_id)
            holders = self.holder_repo.latest_for_token(evaluation.token_id)
            if token is None:
                continue

            text = _format_telegram_message(
                symbol=token.symbol,
                name=token.name,
                token_address=token.token_address,
                liquidity_usd=pair.liquidity_usd if pair else None,
                volume_5m_usd=pair.volume_5m_usd if pair else None,
                holder_count=holders.holder_count if holders else None,
                top10_holder_percent=holders.top10_holder_percent if holders else None,
                risk_score=evaluation.risk_score,
                watch_score=evaluation.watch_score,
                decision=evaluation.decision,
                reasons=evaluation.reasons_json,
            )
            sent = await self.telegram_client.send_message(text)
            payload = {
                "token_address": token.token_address,
                "risk_score": evaluation.risk_score,
                "watch_score": evaluation.watch_score,
                "decision": evaluation.decision,
            }
            self.alert_repo.create(
                token_id=evaluation.token_id,
                channel="telegram",
                alert_type="watch_signal",
                payload_json=payload,
                status="sent" if sent else "failed",
            )
            if sent:
                stats["alerts_sent"] += 1

        self.db.commit()
        return stats


def _fmt_money(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"${value:,.0f}"


def _fmt_int(value: int | None) -> str:
    return "n/a" if value is None else str(value)


def _fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}%"


def _format_telegram_message(
    symbol: str,
    name: str,
    token_address: str,
    liquidity_usd: float | None,
    volume_5m_usd: float | None,
    holder_count: int | None,
    top10_holder_percent: float | None,
    risk_score: int,
    watch_score: int,
    decision: str,
    reasons: list[str],
) -> str:
    lines = [
        f"[WATCH] {symbol}",
        f"Token: {symbol} ({name})",
        f"Address: {token_address}",
        f"Liquidity: {_fmt_money(liquidity_usd)}",
        f"5m Volume: {_fmt_money(volume_5m_usd)}",
        f"Holders: {_fmt_int(holder_count)}",
        f"Top10: {_fmt_pct(top10_holder_percent)}",
        f"Risk: {risk_score}/100",
        f"Watch: {watch_score}/100",
        f"Decision: {decision}",
        "Reasons:",
    ]
    lines.extend([f"- {r}" for r in reasons[:5]])
    lines.append(f"Screener: https://dexscreener.com/solana/{token_address}")
    return "\n".join(lines)
