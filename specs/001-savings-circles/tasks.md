# Tasks: Savings Circles Creation

**Input**: Design documents from `/specs/001-savings-circles/`
**Prerequisites**: plan.md ✓ spec.md ✓ research.md ✓ data-model.md ✓ contracts/ ✓

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add missing dependencies and finalize project scaffolding

- [ ] T001 Add `python-dateutil==2.9.0` to `requirements.txt`
- [ ] T002 Create `tests/` directory with `__init__.py` and `tests/v1/__init__.py`
- [ ] T003 [P] Create `app/models/__init__.py` (already exists — verify imports are clean)
- [ ] T004 [P] Create `app/schemas/__init__.py` (already exists — verify)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: ORM model + Alembic migration that all stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create `SavingsCircle` ORM model in `app/models/circle.py` — fields per `data-model.md`: id (UUID str), creator_id, name, amount (Numeric 18,2), members, frequency, start_date, end_date, payout_count, penalty_percent, grace_period_days, start_when_members, status, created_at
- [ ] T006 Add `import app.models.circle  # noqa: F401` to `alembic/env.py` so Alembic detects the model
- [ ] T007 Generate and review Alembic migration: `alembic revision --autogenerate -m "create savings_circles table"` → save to `alembic/versions/`
- [ ] T008 Add `ix_savings_circles_creator_id` index to the migration (verify autogenerate included it, add manually if not)

**Checkpoint**: Run `alembic upgrade head` — `savings_circles` table must exist with all columns before proceeding

---

## Phase 3: User Story 1 — Create a Savings Circle (Priority: P1) 🎯 MVP

**Goal**: `POST /circles` creates a circle with server-computed end date and returns 201 with full circle data

**Independent Test**: `POST /circles` with valid JWT and body → 201 with `id` and `end_date` present; `POST /circles` with past `start_date` → 422; no token → 401

### Implementation for User Story 1

- [ ] T009 [P] [US1] Create `Frequency` enum and `compute_end_date()` helper in `app/schemas/circle.py` using `dateutil.relativedelta` per `research.md`
- [ ] T010 [P] [US1] Create Pydantic `CreateCircleRequest` schema in `app/schemas/circle.py` — all fields, validators: amount > 0, members >= 2, frequency enum, start_date >= today (`model_validator`), payout_count >= 1, penalty_percent 0–100
- [ ] T011 [US1] Create `CircleResponse` Pydantic schema in `app/schemas/circle.py` — all circle fields including computed `end_date`
- [ ] T012 [US1] Implement `POST /circles` endpoint in `app/api/v1/endpoints/circles.py` — `Depends(get_current_user)`, `Depends(get_db)`, insert `SavingsCircle` with `creator_id = user["id"]` and `end_date = compute_end_date(...)`, return `{"success": True, "data": CircleResponse}` with status 201
- [ ] T013 [US1] Wire `POST /circles` route into `app/api/v1/endpoints/circles.py` alongside existing `GET /circles` stub

**Checkpoint**: `POST /circles` with valid JWT returns 201 with computed `end_date` — US1 complete

---

## Phase 4: User Story 3 — End Date Auto-Computation (Priority: P1, depends on US1)

**Goal**: Verify `compute_end_date` is correct for all 5 frequencies

**Independent Test**: Unit-test `compute_end_date` with the 3 exact scenarios from spec (monthly/4 → 2026-08-01, weekly/4 → 2026-04-29, quarterly/2 → 2026-10-01)

### Implementation for User Story 3

- [ ] T014 [US3] Write unit tests for `compute_end_date` in `tests/v1/test_compute_end_date.py` — cover all 5 frequencies with concrete known-good dates from spec
- [ ] T015 [US3] Run tests and confirm all pass: `pytest tests/v1/test_compute_end_date.py -v`

**Checkpoint**: All 5 frequency computations verified correct — US3 complete

---

## Phase 5: User Story 2 — View Savings Circles (Priority: P2)

**Goal**: `GET /circles` returns authenticated user's circles (empty list when none)

**Independent Test**: Create a circle via POST, then GET → circle appears; fresh user GET → empty list

### Implementation for User Story 2

- [ ] T016 [US2] Implement `GET /circles` in `app/api/v1/endpoints/circles.py` — query `savings_circles` filtered by `creator_id = user["id"]`, return `{"success": True, "data": [CircleResponse, ...]}`
- [ ] T017 [US2] Add `ListCirclesResponse` schema (or reuse list of `CircleResponse`) in `app/schemas/circle.py`

**Checkpoint**: `GET /circles` returns correct list per authenticated user — US2 complete

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T018 [P] Add `GET /health` endpoint to `main.py` returning `{"status": "ok"}`
- [ ] T019 [P] Add `app/api/v1/endpoints/__init__.py` exports if missing
- [ ] T020 Verify nginx route `/api/v1/circle/` → update `lunor-nginx` config to proxy to port 8003
- [ ] T021 [P] Run `docker compose up --build` and smoke-test both endpoints end-to-end
- [ ] T022 Commit all files and update `specs/001-savings-circles/checklists/requirements.md` to mark implementation done

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1 — Create)**: Depends on Phase 2
- **Phase 4 (US3 — End Date)**: Depends on Phase 3 (uses `compute_end_date` from T009)
- **Phase 5 (US2 — List)**: Depends on Phase 2; can run in parallel with Phase 3 once T005–T008 done
- **Phase 6 (Polish)**: Depends on all story phases

### Parallel Opportunities

- T009 and T010 can run in parallel (both in `app/schemas/circle.py` — assign to same dev)
- T003 and T004 can run in parallel
- Phase 3 and Phase 5 can start concurrently once Phase 2 is complete (different devs)
- T018, T019, T021 in Phase 6 can run in parallel

---

## Implementation Strategy

### MVP (User Story 1 only — ~2 hours solo)

1. Phase 1: T001–T004
2. Phase 2: T005–T008 (model + migration)
3. Phase 3: T009–T013 (POST /circles)
4. **STOP and VALIDATE**: `POST /circles` works end-to-end
5. Ship MVP

### Full Delivery

1. MVP above
2. Phase 4: T014–T015 (end date unit tests)
3. Phase 5: T016–T017 (GET /circles)
4. Phase 6: T018–T022 (polish + nginx)

---

## Notes

- `[P]` = can run in parallel with other `[P]` tasks in the same phase
- `[US1/2/3]` maps to user stories in spec.md
- `compute_end_date` lives in `app/schemas/circle.py` alongside the Pydantic schemas (no separate service layer needed — pure function)
- Never accept `end_date` from the client — only `start_date` + `payout_count` + `frequency`
- Always use `user["id"]` from JWT for `creator_id` — never trust a client-supplied user ID
