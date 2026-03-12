"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-03-12
"""


import sqlalchemy as sa

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("chain", sa.String(length=32), nullable=False),
        sa.Column("token_address", sa.String(length=64), nullable=False),
        sa.Column("symbol", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("token_address"),
    )
    op.create_index("ix_tokens_chain", "tokens", ["chain"])
    op.create_index("ix_tokens_token_address", "tokens", ["token_address"])
    op.create_index("ix_tokens_chain_first_seen", "tokens", ["chain", "first_seen_at"])

    op.create_table(
        "pairs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("token_id", sa.Integer(), sa.ForeignKey("tokens.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dex_name", sa.String(length=64), nullable=False),
        sa.Column("pair_address", sa.String(length=64), nullable=False),
        sa.Column("quote_token", sa.String(length=64), nullable=False),
        sa.Column("liquidity_usd", sa.Float(), nullable=True),
        sa.Column("fdv_usd", sa.Float(), nullable=True),
        sa.Column("market_cap_usd", sa.Float(), nullable=True),
        sa.Column("price_usd", sa.Float(), nullable=True),
        sa.Column("volume_5m_usd", sa.Float(), nullable=True),
        sa.Column("volume_1h_usd", sa.Float(), nullable=True),
        sa.Column("buys_5m", sa.Integer(), nullable=True),
        sa.Column("sells_5m", sa.Integer(), nullable=True),
        sa.Column("pair_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_pairs_token_id", "pairs", ["token_id"])
    op.create_index("ix_pairs_pair_address", "pairs", ["pair_address"])
    op.create_index("ix_pairs_snapshot_at", "pairs", ["snapshot_at"])

    op.create_table(
        "token_security",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("token_id", sa.Integer(), sa.ForeignKey("tokens.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mint_authority_renounced", sa.Boolean(), nullable=True),
        sa.Column("freeze_authority_renounced", sa.Boolean(), nullable=True),
        sa.Column("top10_holder_percent", sa.Float(), nullable=True),
        sa.Column("creator_holder_percent", sa.Float(), nullable=True),
        sa.Column("mutable_metadata", sa.Boolean(), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_token_security_token_id", "token_security", ["token_id"])
    op.create_index("ix_token_security_fetched_at", "token_security", ["fetched_at"])

    op.create_table(
        "holder_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("token_id", sa.Integer(), sa.ForeignKey("tokens.id", ondelete="CASCADE"), nullable=False),
        sa.Column("holder_count", sa.Integer(), nullable=True),
        sa.Column("top10_holder_percent", sa.Float(), nullable=True),
        sa.Column("top20_holder_percent", sa.Float(), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_holder_snapshots_token_id", "holder_snapshots", ["token_id"])
    op.create_index("ix_holder_snapshots_fetched_at", "holder_snapshots", ["fetched_at"])

    op.create_table(
        "risk_evaluations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("token_id", sa.Integer(), sa.ForeignKey("tokens.id", ondelete="CASCADE"), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("watch_score", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("reasons_json", sa.JSON(), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_risk_evaluations_token_id", "risk_evaluations", ["token_id"])
    op.create_index("ix_risk_evaluations_decision", "risk_evaluations", ["decision"])
    op.create_index("ix_risk_evaluations_evaluated_at", "risk_evaluations", ["evaluated_at"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("token_id", sa.Integer(), sa.ForeignKey("tokens.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
    )
    op.create_index("ix_alerts_token_id", "alerts", ["token_id"])
    op.create_index("ix_alerts_alert_type", "alerts", ["alert_type"])
    op.create_index("ix_alerts_sent_at", "alerts", ["sent_at"])

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("stats_json", sa.JSON(), nullable=False),
    )
    op.create_index("ix_ingestion_runs_source", "ingestion_runs", ["source"])


def downgrade() -> None:
    op.drop_index("ix_ingestion_runs_source", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")

    op.drop_index("ix_alerts_sent_at", table_name="alerts")
    op.drop_index("ix_alerts_alert_type", table_name="alerts")
    op.drop_index("ix_alerts_token_id", table_name="alerts")
    op.drop_table("alerts")

    op.drop_index("ix_risk_evaluations_evaluated_at", table_name="risk_evaluations")
    op.drop_index("ix_risk_evaluations_decision", table_name="risk_evaluations")
    op.drop_index("ix_risk_evaluations_token_id", table_name="risk_evaluations")
    op.drop_table("risk_evaluations")

    op.drop_index("ix_holder_snapshots_fetched_at", table_name="holder_snapshots")
    op.drop_index("ix_holder_snapshots_token_id", table_name="holder_snapshots")
    op.drop_table("holder_snapshots")

    op.drop_index("ix_token_security_fetched_at", table_name="token_security")
    op.drop_index("ix_token_security_token_id", table_name="token_security")
    op.drop_table("token_security")

    op.drop_index("ix_pairs_snapshot_at", table_name="pairs")
    op.drop_index("ix_pairs_pair_address", table_name="pairs")
    op.drop_index("ix_pairs_token_id", table_name="pairs")
    op.drop_table("pairs")

    op.drop_index("ix_tokens_chain_first_seen", table_name="tokens")
    op.drop_index("ix_tokens_token_address", table_name="tokens")
    op.drop_index("ix_tokens_chain", table_name="tokens")
    op.drop_table("tokens")
