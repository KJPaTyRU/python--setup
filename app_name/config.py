from functools import cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app_name.core.logs import init_logger

levels = ("TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


class PostgresSettings(BaseSettings):
    user: str = "postgres"
    password: str = "postgres"
    db: str = "app_name"


class DbSettings(BaseSettings):
    host: str = "localhost"
    port: str = "5432"
    pool_size: int = 1  # just for async_session context

    driver_schema: str = "postgresql+asyncpg"


class AuthSettings(BaseSettings):
    jwt_access_dt: int = Field(30, ge=0, description="in minutes")
    jwt_refresh_dt: int = Field(60 * 24, ge=0, description="in minutes")


class AppSettings(BaseSettings):
    is_debug: bool = False
    # openssl rand -hex 32
    secret: str = Field(
        "31eca474397470ce766adf655fcdcd7417323d48dc9299e78ad043a8f456ed83",
        min_length=16,
    )

    @computed_field
    @property
    def app_name(self) -> str:
        return "app_name"


class LoggingSettings(BaseSettings):
    level: Literal[levels] = "DEBUG"  # type: ignore


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".prod.env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        env_nested_max_split=1,
    )
    log: LoggingSettings = Field(default_factory=LoggingSettings)

    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    db: DbSettings = Field(default_factory=DbSettings)
    app: AppSettings = Field(default_factory=AppSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)

    @property
    def db_url(self) -> str:
        return (
            f"{self.db.driver_schema}://"
            f"{self.postgres.user}:{self.postgres.password}@"
            f"{self.db.host}:{self.db.port}"
            f"/{self.postgres.db}"
        )


@cache
def get_settings() -> Settings:
    settings = Settings()
    init_logger(settings.log.level)
    return settings
