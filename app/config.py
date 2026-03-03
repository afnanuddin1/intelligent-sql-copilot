from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "flight_copilot"
    postgres_user: str = "copilot_user"
    postgres_password: str = "copilot_pass"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_ttl_results: int = 300
    redis_ttl_suggestions: int = 3600
    openai_api_key: str = ""
    openai_model: str = "llama3.2"
    ollama_base_url: str = "http://localhost:11434/v1"
    app_env: str = "development"
    secret_key: str = "changeme"
    query_timeout_seconds: int = 10
    max_result_rows: int = 500

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
