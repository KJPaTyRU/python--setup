from functools import cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app_name.core.logs import init_logger

levels = ("TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


class PostgresSettings(BaseSettings):
    user: str = "dcs_user"
    password: str = "dcs_password"
    db: str = "dcs_db"


class DbSettings(BaseSettings):
    host: str = "localhost"
    port: str = "5432"
    pool_size: int = 1  # just for async_session context

    driver_schema: str = "postgresql+asyncpg"


class AppSettings(BaseSettings):
    is_debug: bool = False


class LoggingSettings(BaseSettings):
    level: Literal[levels] = "DEBUG"  # type: ignore


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".prod.env"), env_file_encoding="utf-8"
    )
    log: LoggingSettings = Field(default_factory=LoggingSettings)

    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    db: DbSettings = Field(default_factory=DbSettings)

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
