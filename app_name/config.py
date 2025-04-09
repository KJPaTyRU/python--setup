from functools import cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app_name.core.logs import init_logger

levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


class AppSettings(BaseSettings):
    is_debug: bool = False


class LoggingSettings(BaseSettings):
    level: Literal[levels] = "DEBUG"  # type: ignore


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".prod.env"), env_file_encoding="utf-8"
    )
    log: LoggingSettings = Field(default_factory=LoggingSettings)


@cache
def get_settings() -> Settings:
    settings = Settings()
    init_logger(settings.log.level)
    return settings
