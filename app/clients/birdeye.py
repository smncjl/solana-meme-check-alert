import logging
from typing import Any

import httpx

from app.schemas.provider import NormalizedHolders, NormalizedSecurity

logger = logging.getLogger(__name__)


class BirdeyeClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def fetch_security(self, token_address: str) -> NormalizedSecurity | None:
        url = f"{self.base_url}/defi/token_security"
        payload = await self._request(url, {"address": token_address})
        if payload is None:
            return None
        data = payload.get("data") or {}
        return NormalizedSecurity(
            mint_authority_renounced=_as_bool(data.get("mintAuthorityDisabled")),
            freeze_authority_renounced=_as_bool(data.get("freezeAuthorityDisabled")),
            top10_holder_percent=_as_float(data.get("top10HolderPercent")),
            creator_holder_percent=_as_float(data.get("creatorPercent")),
            mutable_metadata=_as_bool(data.get("isMutable")),
            raw_payload_json=payload,
        )

    async def fetch_holders(self, token_address: str) -> NormalizedHolders | None:
        url = f"{self.base_url}/defi/v3/token/holder"
        payload = await self._request(url, {"address": token_address})
        if payload is None:
            return None
        data = payload.get("data") or {}
        return NormalizedHolders(
            holder_count=_as_int(data.get("holderCount")),
            top10_holder_percent=_as_float(data.get("top10HolderPercent")),
            top20_holder_percent=_as_float(data.get("top20HolderPercent")),
            raw_payload_json=payload,
        )

    async def _request(self, url: str, params: dict[str, str]) -> dict | None:
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            logger.warning("birdeye_request_failed url=%s error=%s", url, exc)
            return None

        if not isinstance(payload, dict):
            return None
        return payload


def _as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower = value.lower()
        if lower in {"true", "1", "yes"}:
            return True
        if lower in {"false", "0", "no"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return None
