# Data Model: Savings Circles

**Date**: 2026-03-11 | **Branch**: `001-savings-circles`

## Entity: SavingsCircle

### Table: `savings_circles`

| Column              | Type            | Constraints                        | Notes                               |
|---------------------|-----------------|------------------------------------|-------------------------------------|
| `id`                | VARCHAR(36)     | PK, not null                       | UUID, Python-generated              |
| `creator_id`        | VARCHAR(36)     | not null, indexed                  | JWT `sub` — no FK to another service |
| `name`              | VARCHAR(255)    | not null                           | Not unique per user                 |
| `amount`            | NUMERIC(18,2)   | not null, > 0                      | Per-cycle contribution in ₦         |
| `members`           | INTEGER         | not null, >= 2                     | Target member count                 |
| `frequency`         | VARCHAR(20)     | not null                           | daily/weekly/bi-weekly/monthly/quarterly |
| `start_date`        | DATE            | not null                           | Must be >= today at creation        |
| `end_date`          | DATE            | not null                           | Server-computed, never client-supplied |
| `payout_count`      | INTEGER         | not null, > 0                      | Number of payout cycles             |
| `penalty_percent`   | NUMERIC(5,2)    | not null, default 0, 0–100         | % charged for late contribution     |
| `grace_period_days` | INTEGER         | not null, default 0, >= 0          | Days before penalty applies         |
| `start_when_members`| BOOLEAN         | not null, default false            | Delay start until all members join  |
| `status`            | VARCHAR(20)     | not null, default 'pending'        | pending / active / completed        |
| `created_at`        | TIMESTAMP(TZ)   | not null, server_default=now()     |                                     |

### Indexes
- `ix_savings_circles_creator_id` on `creator_id` — for fast list queries per user

### Status Transitions
```
pending → active    (when start_date reached OR all members joined, if start_when_members=true)
active  → completed (when payout_count cycles have elapsed)
```
Status transitions are out of scope for this feature (MVP only creates in `pending`).

## Validation Rules (enforced in Pydantic schema)

| Field              | Rule                                                    |
|--------------------|---------------------------------------------------------|
| `name`             | 1–255 chars, non-empty after strip                      |
| `amount`           | > 0                                                     |
| `members`          | >= 2                                                    |
| `frequency`        | one of: daily, weekly, bi-weekly, monthly, quarterly    |
| `start_date`       | >= date.today()                                         |
| `payout_count`     | >= 1                                                    |
| `penalty_percent`  | 0 <= x <= 100, default 0                                |
| `grace_period_days`| >= 0, default 0                                         |
| `start_when_members`| bool, default false                                    |
