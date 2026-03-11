# lunor-circle — Savings Circles Service

## Stack
- FastAPI + PostgreSQL (async SQLAlchemy 2.0) + Redis + Alembic
- Python 3.12, Pydantic v2, async/await throughout
- Port: 8003 externally (8003:8000 in docker-compose), root-path `/api/v1/circle`

## Project layout
```
app/
  config.py                ← Pydantic Settings (.env)
  db/
    base.py                ← SQLAlchemy DeclarativeBase
    session.py             ← AsyncSessionLocal engine
  core/
    dependencies.py        ← decode_token(), get_current_user(), get_db()
    exceptions.py          ← AppError(HTTPException)
  models/                  ← SQLAlchemy ORM (no FK to any other service)
  schemas/                 ← Pydantic request/response schemas
  api/v1/
    router.py              ← Top-level v1 router
    endpoints/
      circles.py           ← GET /circles, POST /circles
alembic/versions/          ← Migration scripts
main.py                    ← FastAPI app, lifespan (Redis init)
```

## Key design decisions
- **No FK to other services** — separate PostgreSQL DB, uses `user_id` string (UUID) from JWT
- **JWT validation** — same secret as lunor-auth, validates `type="access"`, decodes `sub` as user_id
- **Balance amounts in naira** — `Numeric(18,2)`, never integer kobo
- **End date computed server-side** — derived from `start_date + payout_count × frequency`, never client-supplied
- **No repositories/ layer** — services query DB directly via AsyncSession (same pattern as lunor-wallet)

## Endpoint pattern
```python
@router.post("", status_code=status.HTTP_201_CREATED, response_model=SomeResponse)
async def create_circle(
    body: SomeRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    ...
```

## Frequency → interval mapping
| Frequency  | Interval            |
|------------|---------------------|
| daily      | +N days             |
| weekly     | +N × 7 days         |
| bi-weekly  | +N × 14 days        |
| monthly    | +N months           |
| quarterly  | +N × 3 months       |

## Alembic
- Folder: `alembic/versions/`
- Always add model imports to `alembic/env.py` before running autogenerate
- Run `alembic upgrade head` on deploy (done automatically in docker-compose command)

## What NOT to do
- Never store amounts as integer kobo — use `Numeric(18,2)` naira
- Never add FK to lunor-auth or lunor-wallet tables
- Never accept client-supplied end dates — always compute server-side
- Never trust client-supplied user_id — decode from JWT via `decode_token()`
- Never auto-generate Alembic migration without reviewing the diff

## Active Technologies
- Python 3.12 + FastAPI 0.115, SQLAlchemy 2.0 (async), Pydantic v2, python-jose, asyncpg, Alembic (001-savings-circles)
- PostgreSQL 16 (separate DB: `lunor_circle`), Redis 7 (separate instance, for future use) (001-savings-circles)

## Recent Changes
- 001-savings-circles: Added Python 3.12 + FastAPI 0.115, SQLAlchemy 2.0 (async), Pydantic v2, python-jose, asyncpg, Alembic
