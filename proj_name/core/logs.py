import sys

from loguru import logger

LOGGER_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<yellow>{process}</yellow> | "
    "<level>{level: ^7}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


def init_logger(log_level: str) -> None:
    logger.remove()
    logger.add(
        sys.stderr, colorize=True, format=LOGGER_FORMAT, level=log_level
    )
