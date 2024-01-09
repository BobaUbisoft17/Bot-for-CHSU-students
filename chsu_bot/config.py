"""Модуль для получения необходимых для работы значений."""

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Получение значения переменных из окружения."""

    ADMIN: int
    BOTTOKEN: str
    RUNTYPE: str = "polling"
    DBURL: str = "./bot.db"
    DOMEN: str = "127.0.0.1"
    HOST: str = "localhost"
    PORT: int = 8080
