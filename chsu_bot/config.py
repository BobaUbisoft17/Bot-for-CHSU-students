"""Модуль для получения необходимых для работы значений."""

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Получение значения переменных из окружения."""

    ADMIN: int
    BOTTOKEN: str
    RUNTYPE: str
    DBURL: str
    DOMEN: str
    HOST: str
    PORT: int
