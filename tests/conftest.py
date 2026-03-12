import os
from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SCHEDULER_ENABLED", "false")
os.environ.setdefault("DISCOVERY_ENABLED", "false")
os.environ.setdefault("ENRICHMENT_ENABLED", "false")
os.environ.setdefault("ALERTING_ENABLED", "false")

from app.api.deps import db_session
from app.main import app
from app.models import HolderSnapshot, Pair, RiskEvaluation, Token, TokenSecurity
from app.models.base import Base


@pytest.fixture(scope="session")
def test_engine() -> Generator:
    engine = create_engine("sqlite:///./test.db", future=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(test_engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, future=True)
    session = TestingSessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db: Session):
    def override_db():
        yield db

    app.dependency_overrides[db_session] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seeded_token(db: Session) -> Token:
    token = Token(
        chain="solana",
        token_address="So11111111111111111111111111111111111111112",
        symbol="TEST",
        name="Test Token",
        first_seen_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(token)
    db.flush()

    pair = Pair(
        token_id=token.id,
        dex_name="raydium",
        pair_address="pair111",
        quote_token="USDC",
        liquidity_usd=60000,
        fdv_usd=1000000,
        market_cap_usd=500000,
        price_usd=0.01,
        volume_5m_usd=25000,
        volume_1h_usd=120000,
        buys_5m=120,
        sells_5m=80,
        pair_created_at=datetime.utcnow(),
        snapshot_at=datetime.utcnow(),
    )
    security = TokenSecurity(
        token_id=token.id,
        mint_authority_renounced=True,
        freeze_authority_renounced=True,
        top10_holder_percent=20.0,
        creator_holder_percent=5.0,
        mutable_metadata=False,
        raw_payload_json={"ok": True},
        fetched_at=datetime.utcnow(),
    )
    holders = HolderSnapshot(
        token_id=token.id,
        holder_count=400,
        top10_holder_percent=20.0,
        top20_holder_percent=35.0,
        raw_payload_json={"ok": True},
        fetched_at=datetime.utcnow(),
    )
    evaluation = RiskEvaluation(
        token_id=token.id,
        risk_score=20,
        watch_score=80,
        decision="ALERT",
        reasons_json=["liquidity acceptable"],
        evaluated_at=datetime.utcnow(),
    )
    db.add_all([pair, security, holders, evaluation])
    db.commit()
    db.refresh(token)
    return token
