import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.schemas.provider import NormalizedPair

logger = logging.getLogger(__name__)


class DexscreenerClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def fetch_latest_solana_pairs(self) -> list[NormalizedPair]:
        profiles_url = f"{self.base_url}/token-profiles/latest/v1"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                profiles_resp = await client.get(profiles_url)
                profiles_resp.raise_for_status()
                profiles_payload = profiles_resp.json()

                token_addresses: list[str] = []
                if isinstance(profiles_payload, list):
                    for item in profiles_payload:
                        if not isinstance(item, dict):
                            continue
                        chain = (item.get("chainId") or "").lower()
                        token_address = item.get("tokenAddress")
                        if chain == "solana" and isinstance(token_address, str):
                            token_addresses.append(token_address)

                deduped_addresses = list(dict.fromkeys(token_addresses))[:20]
                raw_pairs: list[dict] = []
                for token_address in deduped_addresses:
                    token_pairs_url = f"{self.base_url}/token-pairs/v1/solana/{token_address}"
                    pairs_resp = await client.get(token_pairs_url)
                    pairs_resp.raise_for_status()
                    pairs_payload = pairs_resp.json()
                    if isinstance(pairs_payload, list):
                        raw_pairs.extend([row for row in pairs_payload if isinstance(row, dict)])
        except Exception as exc:
            logger.warning("dexscreener_fetch_failed error=%s", exc)
            return []

        normalized: list[NormalizedPair] = []
        for item in raw_pairs[:150]:
            base = item.get("baseToken") or {}
            quote = item.get("quoteToken") or {}
            if base.get("address") is None:
                continue

            pair_created = item.get("pairCreatedAt")
            pair_created_at = None
            if isinstance(pair_created, (int, float)):
                pair_created_at = datetime.fromtimestamp(pair_created / 1000, tz=UTC)

            txns_5m = item.get("txns", {}).get("m5", {})
            volume = item.get("volume", {})
            normalized.append(
                NormalizedPair(
                    chain=(item.get("chainId") or "unknown").lower(),
                    token_address=base.get("address", ""),
                    symbol=base.get("symbol", ""),
                    name=base.get("name", ""),
                    dex_name=item.get("dexId", "unknown"),
                    pair_address=item.get("pairAddress", ""),
                    quote_token=quote.get("symbol", ""),
                    liquidity_usd=_safe_float((item.get("liquidity") or {}).get("usd")),
                    fdv_usd=_safe_float(item.get("fdv")),
                    market_cap_usd=_safe_float(item.get("marketCap")),
                    price_usd=_safe_float(item.get("priceUsd")),
                    volume_5m_usd=_safe_float(volume.get("m5")),
                    volume_1h_usd=_safe_float(volume.get("h1")),
                    buys_5m=_safe_int(txns_5m.get("buys")),
                    sells_5m=_safe_int(txns_5m.get("sells")),
                    pair_created_at=pair_created_at,
                )
            )
        return [p for p in normalized if p.chain == "solana"]


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None
