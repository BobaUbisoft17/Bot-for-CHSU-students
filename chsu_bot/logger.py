"""Модуль для создания логов."""

from loguru import logger


logger.add(
    encoding="u8",
    sink="logs/log.log",
    format="{time:DD-MM-YYYY at HH:mm:ss} | {level} | {message}",
    rotation="1 week",
    compression="zip",
    backtrace=False,
    enqueue=True,
)
