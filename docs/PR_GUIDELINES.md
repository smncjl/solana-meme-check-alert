# PR Guidelines

Use this guide for all pull requests in `agent-dev-review-stack`.

## Required PR Structure

1. Title
- Use Conventional Commit format.
- Examples:
  - `feat: add issue_comment command mapping`
  - `fix: prevent duplicate agent jobs on webhook retries`
  - `docs: add runbook for review-worker`

2. Problem Statement
- What is broken/missing?
- Why this change is needed now?

3. Scope
- What is included in this PR?
- What is explicitly not included?

4. Contract Impact
- List changed contract docs:
  - `services/<service>/API_CONTRACT.md`
  - `services/<service>/SERVICE_CONTRACT.md`
  - `docs/contracts/<service>.md`
- If no contract impact, state: `No contract changes`.

5. Test Evidence
- Include exact commands and result:
  - `.venv/bin/ruff check .`
  - `.venv/bin/pyright`
  - `.venv/bin/pytest -q`
- If a check is skipped, explain why.

6. Risk & Rollback
- Main risks to monitor.
- How to revert safely.

7. Follow-ups
- Deferred work, with concise bullets.

## PR Size Guidance
- Prefer PRs under ~400 changed lines when possible.
- Split mixed concerns (feature + refactor + docs) into separate PRs unless tightly coupled.

## Reviewer Checklist
- Scope is clear and bounded.
- Tests cover behavior changes.
- Contracts/docs updated when interfaces changed.
- No unrelated file churn.

## Merge Criteria
- CI green.
- At least one review approval.
- No unresolved critical comments.
