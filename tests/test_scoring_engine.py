from app.scoring.engine import ScoringEngine, ScoringInput


def test_scoring_engine_alert_candidate():
    engine = ScoringEngine()
    result = engine.evaluate(
        ScoringInput(
            liquidity_usd=80000,
            volume_5m_usd=25000,
            buys_5m=100,
            sells_5m=70,
            holder_count=500,
            top10_holder_percent=18,
            creator_holder_percent=3,
            mint_authority_renounced=True,
            freeze_authority_renounced=True,
        )
    )
    assert result.risk_score < 30
    assert result.watch_score >= 70
    assert result.decision == "ALERT"


def test_scoring_engine_reject_candidate():
    engine = ScoringEngine()
    result = engine.evaluate(
        ScoringInput(
            liquidity_usd=5000,
            volume_5m_usd=50000,
            buys_5m=20,
            sells_5m=100,
            holder_count=50,
            top10_holder_percent=45,
            creator_holder_percent=20,
            mint_authority_renounced=False,
            freeze_authority_renounced=False,
        )
    )
    assert result.risk_score >= 70
    assert result.decision == "REJECT"
