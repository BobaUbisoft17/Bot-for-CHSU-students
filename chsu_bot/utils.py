"""Модуль для утилит."""

import datetime


def valid_range_length(start_date: str, end_date: str) -> bool:
    """Проверка временного диапазона на соответствие допустимой длине."""
    start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y")
    end_date = datetime.datetime.strptime(end_date, "%d.%m.%Y")
    return -31 <= (end_date - start_date).days <= 31


def valid_date(fst_date: str, snd_date: str) -> bool:
    """Проверка действительности дат."""
    fst_date = datetime.datetime.strptime(fst_date, "%d.%m.%Y")
    snd_date = datetime.datetime.strptime(snd_date, "%d.%m.%Y")
    return snd_date >= fst_date
