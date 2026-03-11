# API Contract: Circles Endpoints

**Service**: lunor-circle | **Base path**: `/api/v1/circle` (set via nginx + `--root-path`)
**Auth**: Bearer JWT (issued by lunor-auth, HS256)

---

## POST /circles

Create a new savings circle.

### Request

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**
```json
{
  "name": "Family Ajo",
  "amount": 5000.00,
  "members": 6,
  "frequency": "monthly",
  "start_date": "2026-04-01",
  "payout_count": 6,
  "penalty_percent": 5.0,
  "grace_period_days": 3,
  "start_when_members": false
}
```

**Required fields**: `name`, `amount`, `members`, `frequency`, `start_date`, `payout_count`
**Optional fields**: `penalty_percent` (default: 0), `grace_period_days` (default: 0), `start_when_members` (default: false)

### Responses

**201 Created**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Family Ajo",
    "amount": "5000.00",
    "members": 6,
    "frequency": "monthly",
    "start_date": "2026-04-01",
    "end_date": "2026-10-01",
    "payout_count": 6,
    "penalty_percent": "5.00",
    "grace_period_days": 3,
    "start_when_members": false,
    "status": "pending",
    "created_at": "2026-03-11T10:00:00Z"
  }
}
```

**401 Unauthorized** — missing or invalid token
```json
{"detail": "Invalid or expired token."}
```

**422 Unprocessable Entity** — validation failure
```json
{
  "detail": [
    {"loc": ["body", "start_date"], "msg": "start_date must be today or a future date", "type": "value_error"}
  ]
}
```

### Validation errors

| Condition                        | HTTP | Message                                          |
|----------------------------------|------|--------------------------------------------------|
| Missing required field           | 422  | Field required                                   |
| `amount` <= 0                    | 422  | Input should be greater than 0                   |
| `members` < 2                    | 422  | Input should be greater than or equal to 2       |
| `frequency` not in allowed list  | 422  | Input should be 'daily', 'weekly', ...           |
| `start_date` in the past         | 422  | start_date must be today or a future date        |
| `payout_count` < 1               | 422  | Input should be greater than or equal to 1       |
| `penalty_percent` > 100          | 422  | Input should be less than or equal to 100        |

---

## GET /circles

Retrieve the authenticated user's savings circles.

### Request

**Headers**
```
Authorization: Bearer <access_token>
```

### Responses

**200 OK**
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Family Ajo",
      "amount": "5000.00",
      "members": 6,
      "frequency": "monthly",
      "start_date": "2026-04-01",
      "end_date": "2026-10-01",
      "payout_count": 6,
      "penalty_percent": "5.00",
      "grace_period_days": 3,
      "start_when_members": false,
      "status": "pending",
      "created_at": "2026-03-11T10:00:00Z"
    }
  ]
}
```

**200 OK** (no circles)
```json
{"success": true, "data": []}
```

**401 Unauthorized**
```json
{"detail": "Invalid or expired token."}
```
