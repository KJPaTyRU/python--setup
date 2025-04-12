from functools import cache
import sys
from typing import Literal

from loguru import logger
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app_name.core.logs import init_logger

levels = ("TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


class AppBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")


class PostgresSettings(AppBaseSettings):
    user: str = "postgres"
    password: str = "postgres"
    db: str = "app_name"


class DbSettings(AppBaseSettings):
    host: str = "localhost"
    port: str = "5432"
    pool_size: int = 1  # just for async_session context

    driver_schema: str = "postgresql+asyncpg"


class AuthSettings(AppBaseSettings):
    jwt_access_dt: int = Field(30, ge=0, description="in minutes")
    jwt_refresh_dt: int = Field(60 * 24, ge=0, description="in minutes")


class AppSettings(AppBaseSettings):
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


class LoggingSettings(AppBaseSettings):
    level: Literal[levels] = "DEBUG"  # type: ignore


class Settings(AppBaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_prefix="", env_nested_delimiter="_"
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


class AlembicSettings(AppBaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_prefix="", env_nested_delimiter="_"
    )
    db: DbSettings = Field(default_factory=DbSettings)
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)

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
    if "alembic" in sys.argv[0]:
        return AlembicSettings()
    settings = Settings()
    init_logger(settings.log.level)
    logger.info("[Settings] Settings has been successfully loaded!")
    return settings
