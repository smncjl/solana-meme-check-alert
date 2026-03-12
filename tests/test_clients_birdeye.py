import pytest
import respx
from httpx import Response

from app.clients.birdeye import BirdeyeClient


@pytest.mark.asyncio
@respx.mock
async def test_birdeye_client_normalizes_security_and_holders():
    respx.get("https://public-api.birdeye.so/defi/token_security").mock(
        return_value=Response(
            200,
            json={
                "data": {
                    "mintAuthorityDisabled": True,
                    "freezeAuthorityDisabled": True,
                    "top10HolderPercent": 21.5,
                    "creatorPercent": 4.0,
                    "isMutable": False,
                }
            },
        )
    )
    respx.get("https://public-api.birdeye.so/defi/v3/token/holder").mock(
        return_value=Response(
            200,
            json={"data": {"holderCount": 420, "top10HolderPercent": 21.5, "top20HolderPercent": 35.4}},
        )
    )

    client = BirdeyeClient("https://public-api.birdeye.so", "key")
    security = await client.fetch_security("token")
    holders = await client.fetch_holders("token")

    assert security is not None
    assert security.mint_authority_renounced is True
    assert holders is not None
    assert holders.holder_count == 420
