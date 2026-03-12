# AGENTS.md

Repository-wide operating rules for `aurora`.

## Workflow Rules
- Branch from `main` for every change.
- Keep PRs small and scoped to one concern.
- Run local quality gates before commit.
- Update service docs and centralized contracts in the same change.

## Branch Rules
- Branch naming:
  - `feat/<short-scope>`
  - `fix/<short-scope>`
  - `chore/<short-scope>`
  - `docs/<short-scope>`
- Never commit directly to `main` except repository bootstrapping emergencies.
- Rebase feature branches onto latest `main` before opening PR.

## Commit Rules
- Use Conventional Commit style:
  - `feat: ...`
  - `fix: ...`
  - `chore: ...`
  - `docs: ...`
  - `test: ...`
- Keep commits atomic and reviewable.
- Include docs updates when interfaces or behavior change.

## Test Rules
- Required before pushing:
  - `.venv/bin/ruff check .`
  - `.venv/bin/pyright`
  - `.venv/bin/pytest -q`
- New mapping/routing logic must include tests.
- Bug fixes must include either a regression test or a note in `TEST_PLAN.md` explaining why not.

## PR Rules
- PR title should follow Conventional Commit style.
- PR description must include:
  - Problem statement
  - Scope
  - Test evidence (commands + outcome)
  - Follow-ups (if deferred)
- Link changed contracts:
  - `services/<service>/API_CONTRACT.md`
  - `services/<service>/SERVICE_CONTRACT.md`
  - `docs/contracts/<service>.md`
- Use PR documentation guide:
  - `docs/PR_GUIDELINES.md`

## Service Governance Rules
Each service must maintain these files:
- `API_CONTRACT.md`
- `CHANGELOG.md`
- `README.md`
- `RUNBOOK.md`
- `SERVICE_CONTRACT.md`
- `TEST_PLAN.md`


## Data/Queue Namespace Rules
- Every service defines a Postgres schema owner name (even if data is shared in PoC).
- Every service defines a Redis namespace prefix for keys/queues.
- Naming convention:
  - DB schema: snake_case service name (example: `webhook_api`)
  - Redis namespace: `<service>:` (example: `webhook-api:`)
