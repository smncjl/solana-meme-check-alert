import re

import pytest
import respx
from httpx import Response

from app.clients.dexscreener import DexscreenerClient


@pytest.mark.asyncio
@respx.mock
async def test_dexscreener_client_normalizes_pairs():
    profiles_payload = [
        {
            "chainId": "solana",
            "tokenAddress": "So11111111111111111111111111111111111111112",
        }
    ]
    pairs_payload = [
        {
            "chainId": "solana",
            "dexId": "raydium",
            "pairAddress": "pair1",
            "baseToken": {
                "address": "So11111111111111111111111111111111111111112",
                "symbol": "ABC",
                "name": "Alpha",
            },
            "quoteToken": {"symbol": "USDC"},
            "liquidity": {"usd": 100000},
            "volume": {"m5": 25000, "h1": 150000},
            "txns": {"m5": {"buys": 20, "sells": 10}},
        }
    ]
    respx.get("https://api.dexscreener.com/token-profiles/latest/v1").mock(
        return_value=Response(200, json=profiles_payload)
    )
    respx.get(
        re.compile(r"https://api\.dexscreener\.com/token-pairs/v1/solana/.+")
    ).mock(
        return_value=Response(200, json=pairs_payload)
    )

    client = DexscreenerClient("https://api.dexscreener.com")
    rows = await client.fetch_latest_solana_pairs()

    assert len(rows) == 1
    assert rows[0].token_address == "So11111111111111111111111111111111111111112"
    assert rows[0].liquidity_usd == 100000


@pytest.mark.asyncio
@respx.mock
async def test_dexscreener_client_handles_profile_failure():
    respx.get("https://api.dexscreener.com/token-profiles/latest/v1").mock(
        return_value=Response(404, json={})
    )

    client = DexscreenerClient("https://api.dexscreener.com")
    rows = await client.fetch_latest_solana_pairs()

    assert rows == []
