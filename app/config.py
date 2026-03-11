from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool = True

    # ── JWT (must match lunor-auth) ────────────────────────────────────────────
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"

    # ── Database (separate from all other services) ────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lunor_circle"

    # ── Redis (dedicated instance for lunor-circle) ────────────────────────────
    redis_url: str = "redis://localhost:6379"

    model_config = {"env_file": ".env"}


settings = Settings()
