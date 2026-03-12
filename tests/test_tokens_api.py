def test_list_tokens(client, seeded_token):
    resp = client.get("/api/v1/tokens?limit=10")
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload) >= 1
    assert payload[0]["token_address"] == seeded_token.token_address
    assert payload[0]["recommended_action"] == "SEND_ALERT"


def test_get_token_detail(client, seeded_token):
    resp = client.get(f"/api/v1/tokens/{seeded_token.token_address}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["symbol"] == "TEST"
    assert body["latest_pair"]["liquidity_usd"] == 60000
    assert body["latest_evaluation"]["decision"] == "ALERT"
    assert body["latest_evaluation"]["recommended_action"] == "SEND_ALERT"


def test_stats_summary(client, seeded_token):
    resp = client.get("/api/v1/stats/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["tokens_tracked"] >= 1
    assert body["evaluations_total"] >= 1
