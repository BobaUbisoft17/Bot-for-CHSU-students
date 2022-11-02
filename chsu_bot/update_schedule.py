"""Модуль обновления расписания в БД."""

import asyncio
import datetime

from db import get_group_ids, update_group_schedule
from logger import logger
from parse import get_schedule


async def update_schedule(update_time: int) -> None:
    """Получение расписания."""
    await asyncio.sleep(update_time)
    logger.info("Начался процесс обновления расписания")
    group_ids = await get_group_ids()
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
        "%d.%m.%Y"
    )
    for i in range(0, len(group_ids), 60):
        await asyncio.gather(
            *[
                reload_group_schedule(group_id, today, tomorrow)
                for group_id in group_ids[i : i + 60]
            ]
        )
        await asyncio.sleep(5)
    logger.info("Расписание успешно обнолвено")


async def reload_group_schedule(
    group_id: int, today: str, tomorrow: str
) -> None:
    """Парсинг json в расписание, и его отправка в БД."""
    schedules = await get_schedule(group_id, today, tomorrow)
    await update_group_schedule(schedules, group_id)


async def loop_update_schedule() -> None:
    """Обновление расписания в бесконечном цикле."""
    while True:
        await update_schedule(21600)
