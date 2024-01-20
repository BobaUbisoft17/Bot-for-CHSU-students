"""Модуль обновления расписания в БД."""

import asyncio
import datetime

from db import Groups
from loguru._logger import Logger
from parse import ChsuAPI
from schedule import Schedule


class Reloader:
    """Класс обновления расписания."""

    def __init__(
        self,
        logger: Logger,
        api: ChsuAPI,
        schedule: Schedule,
        group_storage: Groups,
    ) -> None:
        self.logger = logger
        self.api = api
        self.schedule = schedule
        self.group_storage = group_storage

    async def reload_schedule(self, waiting_time: int = 0) -> None:
        """Обновление расписания."""
        await asyncio.sleep(waiting_time)
        self.logger.info("Начался процесс обновления расписания")
        schedules = []
        unparsed_schedule = await self.api.get_all_groups_schedule()
        collect_schedule = self.collect_schedule_by_ids_and_dates(
            unparsed_schedule
        )
        for group_id in collect_schedule.keys():
            today, tomorrow = self.split_schedule(collect_schedule[group_id])
            schedules.append(
                [
                    self.schedule.render(today),
                    self.schedule.render(tomorrow),
                    group_id,
                ]
            )

        for group_id in await self.group_storage.unused_id(
            list(collect_schedule)
        ):
            schedules.append(
                [self.schedule.render([]), self.schedule.render([]), group_id]
            )

        await self.group_storage.update_groups_schedule(schedules)

        self.logger.info("Расписание успешно обнолвено")

    async def loop_update_schedule(self) -> None:
        """Цикл обновления расписания."""
        while True:
            await self.reload_schedule(self.get_waiting_time())

    @staticmethod
    def collect_schedule_by_ids_and_dates(schedule: dict) -> dict:
        """Фасовка пар по группам и датам."""
        collected_schedule = {}
        for lecture in schedule:
            for group in lecture["groups"]:
                group_id = group["id"]
                if collected_schedule.get(group_id) is None:
                    collected_schedule[group_id] = {}

                date = lecture["dateEvent"]
                if collected_schedule[group_id].get(date) is None:
                    collected_schedule[group_id][date] = []

                collected_schedule[group_id][date].append(lecture)

        return collected_schedule

    @staticmethod
    def split_schedule(
        schedule: dict[str, dict[str, list[dict[str, str]]]]
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        """Разбиение полученного расписания на два дня."""
        dates = list(schedule)
        if len(schedule) == 2:
            return schedule[dates[0]], schedule[dates[1]]

        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        if dates[0] == current_date:
            return schedule[dates[0]], []
        return [], schedule[dates[0]]

    @staticmethod
    def get_waiting_time() -> int:
        """Расчёт времени ожидания."""
        time_now = datetime.datetime.now()
        next_reload_time = (time_now.hour // 6 + 1) * 6 * 60
        return (next_reload_time - time_now.hour * 60 - time_now.minute) * 60
