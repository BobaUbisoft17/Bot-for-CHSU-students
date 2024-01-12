"""Модуль запуска бота с помощью поллингом."""

import asyncio

from aiogram import Dispatcher


class Polling:
    """Класс управление поллингом."""

    def __init__(self, dp: Dispatcher, tasks: list) -> None:
        self.dp = dp
        self.tasks = tasks

    async def run(self) -> None:
        """Запуск бота."""
        for task in self.tasks:
            asyncio.create_task(task)
        await self.dp.start_polling(fast=True)
