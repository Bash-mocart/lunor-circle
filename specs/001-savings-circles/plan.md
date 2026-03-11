# Implementation Plan: Savings Circles Creation

**Branch**: `001-savings-circles` | **Date**: 2026-03-11 | **Spec**: [spec.md](spec.md)

## Summary

Implement `POST /circles` (create) and `GET /circles` (list) endpoints in the lunor-circle FastAPI microservice. The `SavingsCircle` model is persisted in a dedicated PostgreSQL database. End date is computed server-side from `start_date + payout_count × frequency`. User identity is derived exclusively from the validated JWT — no FK to any other service.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI 0.115, SQLAlchemy 2.0 (async), Pydantic v2, python-jose, asyncpg, Alembic
**Storage**: PostgreSQL 16 (separate DB: `lunor_circle`), Redis 7 (separate instance, for future use)
**Testing**: pytest + pytest-asyncio + httpx (AsyncClient)
**Target Platform**: Linux container (Docker), behind nginx at `/api/v1/circle`
**Project Type**: Web service (microservice)
**Performance Goals**: p95 < 500ms for circle creation under normal load
**Constraints**: No FK to lunor-auth or lunor-wallet; end date never client-supplied; amounts in Naira (Numeric 18,2)
**Scale/Scope**: MVP — single-user circle creation + listing; member-join and payout scheduling out of scope

## Constitution Check

Constitution template not yet filled in — no formal gates defined. Proceeding with project conventions from CLAUDE.md:

- [x] No FK to other services — user_id is a plain string (UUID) from JWT
- [x] Amounts in Naira as Numeric(18,2) — not integer kobo
- [x] End date computed server-side only
- [x] JWT decoded via `get_current_user` dependency — no client-supplied user identity
- [x] Alembic migration required for every model change

## Project Structure

### Documentation (this feature)

```text
specs/001-savings-circles/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/           ← Phase 1 output
│   └── circles-api.md
└── tasks.md             ← Phase 2 output (/speckit.tasks)
```

### Source Code

```text
app/
├── models/
│   └── circle.py           ← SavingsCircle ORM model
├── schemas/
│   └── circle.py           ← CreateCircleRequest, CircleResponse
├── api/v1/endpoints/
│   └── circles.py          ← GET /circles, POST /circles
alembic/versions/
│   └── 001_create_savings_circles.py
tests/
├── v1/
│   └── test_circles.py
```
