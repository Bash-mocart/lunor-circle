from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = True

    # ── JWT (must match lunor-auth) ────────────────────────────────────────────
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"

    # ── Database (separate from all other services) ────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lunor_circle"

    # ── Redis (dedicated instance for lunor-circle internal use) ──────────────
    redis_url: str = "redis://localhost:6379"

    # ── Event bus Redis (shared across all Lunor services for Pub/Sub) ─────────
    event_bus_url: str = "redis://localhost:6380/0"

    # ── lunor-matrix internal URL (for room_id lookups) ───────────────────────
    lunor_matrix_url: str = ""  # e.g. http://172.17.0.1:8004

    model_config = {"env_file": ".env"}


settings = Settings()
