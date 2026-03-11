# Quickstart: lunor-circle

## Prerequisites
- Docker + Docker Compose
- A valid JWT secret (must match lunor-auth's `JWT_SECRET_KEY`)

## 1. Environment
```bash
cp .env.example .env
# Edit .env — set JWT_SECRET_KEY to match lunor-auth
```

## 2. Run
```bash
docker compose up --build
```
Service available at `http://localhost:8003` (nginx routes `/api/v1/circle/*` in production).

## 3. Verify
```bash
curl http://localhost:8003/docs
```

## 4. Create a circle (example)
```bash
curl -X POST http://localhost:8003/circles \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Ajo",
    "amount": 10000,
    "members": 4,
    "frequency": "monthly",
    "start_date": "2026-05-01",
    "payout_count": 4
  }'
```

## 5. Run tests (once test suite is added)
```bash
# From repo root with venv active
pytest tests/ -v
```

## Local dev (without Docker)
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Set env vars in .env, then:
alembic upgrade head
uvicorn main:app --reload --port 8003
```
