"""Модуль запуска бота с помощью поллингом."""

from aiogram import Dispatcher


class Polling:
    """Класс управление поллингом."""

    def __init__(self, dp: Dispatcher, tasks: list) -> None:
        self.dp = dp
        self.tasks = tasks

    async def run(self) -> None:
        """Запуск бота."""
        await self.dp.start_polling(fast=True)
