"""Модуль для получения необходимых для работы значений."""

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Получение значения переменных из окружения."""

    ADMIN: int
    BOTTOKEN: str
    RUNTYPE: str
    DBURL: str
    DOMEN: str = "127.0.0.1"
    HOST: str = "0.0.0.0"
    PORT: int = 8080
