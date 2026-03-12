# solana-rug-guard

Lightweight Solana meme-token risk analytics and alerting MVP.

This project ingests new Solana pairs, enriches token risk metadata, computes deterministic rug-risk/watch scores, and sends Telegram alerts for candidates that pass safety filters.

## Scope

Included in v1:
- Dexscreener polling ingestion for Solana pairs
- Birdeye security + holder enrichment
- Deterministic configurable scoring (risk/watch)
- PostgreSQL persistence with Alembic migration
- FastAPI endpoints for tokens, token details, alerts, summary stats
- Telegram alert delivery with duplicate-alert prevention
- APScheduler jobs for periodic workflow

Not included:
- auto trading or transaction execution
- wallet signing/private key management
- copy trading, auth, billing, advanced ML

## Architecture

```text
app/
  api/        # REST endpoints
  core/       # config, database, logging, scheduler
  models/     # SQLAlchemy ORM models
  schemas/    # API and provider DTO schemas
  repos/      # persistence access layer
  clients/    # external API clients
  services/   # orchestration business logic
  jobs/       # scheduled tasks
  scoring/    # deterministic scoring rules + engine
```

Provider contracts are isolated in `app/clients/*` and normalized into internal schemas (`app/schemas/provider.py`) before service usage.

## Data Model

Initial schema includes:
- `tokens`
- `pairs`
- `token_security`
- `holder_snapshots`
- `risk_evaluations`
- `alerts`
- `ingestion_runs`

Migration: `alembic/versions/0001_initial_schema.py`.

## Scoring

`app/scoring/engine.py` computes:
- `risk_score` (0 safer -> 100 dangerous)
- `watch_score` (0 ignore -> 100 interesting)
- `decision`: `REJECT`, `CAUTION`, `WATCH`, `ALERT`

Rules are centralized in `app/scoring/rules.py` for easy configuration.

Decision-to-action mapping (also exposed as `recommended_action` in token APIs):
- `REJECT` -> `IGNORE_TOKEN` (drop from consideration)
- `CAUTION` -> `MONITOR_WAIT` (re-evaluate later, no alert)
- `WATCH` -> `ADD_TO_WATCHLIST` (monitor actively)
- `ALERT` -> `SEND_ALERT` (notify now)
- no evaluation yet -> `INSUFFICIENT_DATA`

## Jobs and Schedule

Configured in `app/main.py` + `app/core/config.py`.

Default intervals:
- discover pairs: 60s
- enrich security: 120s
- evaluate tokens: 120s
- send alerts: 60s

Jobs:
- `discover_pairs`
- `enrich_security`
- `evaluate_tokens`
- `send_alerts`

Use `SCHEDULER_ENABLED=false` for tests/local API-only execution.

## API

- `GET /health`
- `GET /api/v1/tokens?limit=50&decision=WATCH`
- `GET /api/v1/tokens/{token_address}`
- `GET /api/v1/alerts?limit=50`
- `GET /api/v1/stats/summary`

`/api/v1/tokens` and token detail responses include:
- `decision`
- `recommended_action`
- `risk_score`
- `watch_score`

## Configuration

Copy and edit `.env.example` or export env vars:

- `APP_ENV`
- `DATABASE_URL`
- `DEXSCREENER_BASE_URL`
- `BIRDEYE_BASE_URL`
- `BIRDEYE_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `DISCOVERY_ENABLED`
- `ENRICHMENT_ENABLED`
- `ALERTING_ENABLED`
- `MIN_WATCH_SCORE`
- `MAX_RISK_SCORE_FOR_ALERT`

## Run with Docker Compose

```bash
docker compose up --build
```

Run migration in app container:

```bash
docker compose exec api alembic upgrade head
```

## Local Dev

```bash
make install
alembic upgrade head
make run
```

## Testing

```bash
make test
```

Current test coverage focuses on:
- scoring engine behavior
- API basics
- mocked Dexscreener/Birdeye clients
- Telegram alert duplicate prevention

## Roadmap

- optional minimal admin UI
- websocket ingestion source support
- richer historical trend metrics and anomaly policies
- provider backoff/retry policy tuning
