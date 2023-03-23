"""Модуль обновления расписания в БД."""

import asyncio
import datetime

from database.group_db import get_group_ids, update_group_schedule
from logger import logger
from parse import get_schedule
from typing import Dict, Tuple


async def update_schedule(waiting_time: int) -> None:
    """Получение расписания."""
    await asyncio.sleep(waiting_time)
    logger.info("Начался процесс обновления расписания")
    group_ids = await get_group_ids()
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    tomorrow = (
        datetime.datetime.now() + datetime.timedelta(days=1)
    ).strftime("%d.%m.%Y")
    for i in range(0, len(group_ids), 60):
        schedules = await asyncio.gather(
            *[
                reload_group_schedule(group_id, today, tomorrow)
                for group_id in group_ids[i : i + 60]
            ]
        )
        await update_group_schedule(schedules)
        await asyncio.sleep(5)
    logger.info("Расписание успешно обнолвено")


async def reload_group_schedule(
    group_id: int, today: str, tomorrow: str
) -> Tuple[str, Dict[str, str]]:
    """Парсинг json в расписание, и его отправка в БД."""
    schedules = await get_schedule(group_id, today, tomorrow)
    return group_id, schedules


async def loop_update_schedule() -> None:
    """Обновление расписания в бесконечном цикле."""
    while True:
        now = datetime.datetime.now()

        waiting_time = (
            6 * (now.hour // 6 + 1) * 60 + 1 - (now.hour * 60 + now.minute)
        ) * 60
        await update_schedule(waiting_time)
