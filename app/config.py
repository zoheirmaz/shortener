from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    code_pool_target_available: int = 1000
    reserved_code_timeout_seconds: int = 300

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
