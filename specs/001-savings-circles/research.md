# Research: Savings Circles Creation

**Date**: 2026-03-11 | **Branch**: `001-savings-circles`

## End Date Computation

**Decision**: Use Python `dateutil.relativedelta` for month/quarter arithmetic; `timedelta` for day/week.

**Rationale**: `relativedelta` handles month-end edge cases correctly (e.g. Jan 31 + 1 month = Feb 28, not Mar 3). Plain `timedelta` is wrong for calendar months.

**Implementation**:
```python
from datetime import date
from datetime import timedelta
from dateutil.relativedelta import relativedelta

FREQUENCY_INTERVALS = {
    "daily":      lambda n: relativedelta(days=n),
    "weekly":     lambda n: relativedelta(weeks=n),
    "bi-weekly":  lambda n: relativedelta(weeks=n * 2),
    "monthly":    lambda n: relativedelta(months=n),
    "quarterly":  lambda n: relativedelta(months=n * 3),
}

def compute_end_date(start: date, payout_count: int, frequency: str) -> date:
    delta = FREQUENCY_INTERVALS[frequency](payout_count)
    return start + delta
```

**Dependency to add**: `python-dateutil==2.9.0` to requirements.txt.

---

## UUID Primary Key Strategy

**Decision**: Use PostgreSQL `gen_random_uuid()` via SQLAlchemy `server_default`.

**Rationale**: Avoids Python-side UUID generation inconsistencies; UUIDs are returned in response as strings. Consistent with how lunor-wallet handles IDs.

**Implementation**:
```python
import uuid
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

id: Mapped[str] = mapped_column(
    String(36), primary_key=True, default=lambda: str(uuid.uuid4())
)
```

---

## Circle Status Enum

**Decision**: `pending` → `active` → `completed`. Use Python `enum.Enum` stored as VARCHAR in DB (not PG ENUM type).

**Rationale**: VARCHAR avoids PG ENUM migration complexity (ALTER TYPE required for new values). Consistent with lunor-wallet pattern.

**Default on creation**: `pending` — circle waits for members or start date.

---

## Validation — Start Date in the Past

**Decision**: Validate in Pydantic `model_validator` using `date.today()`.

**Rationale**: Pydantic v2 validators run before the endpoint body is touched, giving clean 422 responses at the serialization layer without service-layer code.

```python
from pydantic import model_validator
from datetime import date

@model_validator(mode="after")
def start_date_not_in_past(self) -> "CreateCircleRequest":
    if self.start_date < date.today():
        raise ValueError("start_date must be today or a future date")
    return self
```

---

## No Repository Layer

**Decision**: Endpoint functions query `AsyncSession` directly (same pattern as lunor-wallet).

**Rationale**: CLAUDE.md explicitly states no repositories/ layer. Adding one for 2 endpoints is over-engineering. Direct session use is simpler and consistent with the rest of the codebase.

---

## Testing Strategy

**Decision**: pytest + `httpx.AsyncClient` with a real test database (not mocks).

**Rationale**: Integration tests with a real DB catch migration issues that mock-DB tests miss. Use `pytest-asyncio` with `asyncio_mode = "auto"`.

**Test DB**: `lunor_circle_test` — created/dropped per test session via Alembic.
