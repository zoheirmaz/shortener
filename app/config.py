from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_type: str = "sqlite"

    sqlite_path: str = "./shortener.db"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "shortener"

    code_pool_target_available: int = 1000
    reserved_code_timeout_seconds: int = 300

    cache_ttl_seconds: int = 3600

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    redis_cache_url: str = "redis://localhost:6379/1"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def database_url(self) -> str:
        if self.database_type.lower() == "postgres":
            return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        return f"sqlite:///{self.sqlite_path}"


settings = Settings()
