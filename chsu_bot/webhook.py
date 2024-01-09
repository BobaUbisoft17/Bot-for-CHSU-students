"""Модуль для настройки webhook."""

import asyncio

import aiogram
from aiogram import types
from fastapi import FastAPI
from logger import logger
import uvicorn


class Webhook:
    """Класс для управления вебхуком."""

    def __init__(
        self,
        dp: aiogram.Dispatcher,
        bot: aiogram.Bot,
        tasks: list,
        webhook_path: str,
        webhook_host: str,
        host: str,
        port: int,
    ) -> None:
        self.app = FastAPI()
        self.webhook_host = webhook_host
        self.webhook_path = webhook_path
        self.webhook_url = self.webhook_host + self.webhook_path
        self.host = host
        self.port = port
        self.dp = dp
        self.bot = bot
        self.tasks = tasks

        self.app.add_event_handler("startup", self.on_startup)
        self.app.add_event_handler("shutdown", self.on_shutdown)

        self.app.add_api_route(
            self.webhook_url, endpoint=self.start_webhook, methods=["POST"]
        )

    async def on_startup(self) -> None:
        """Задачи, выполняющиеся перед запуском приложения."""
        webhook_info = await self.bot.get_webhook_info()
        if webhook_info.url != self.webhook_url:
            await self.bot.set_webhook(url=self.webhook_url)
        for task in self.tasks:
            asyncio.create_task(task)

        logger.info("Запуск бота")

    async def on_shutdown(self) -> None:
        """Задачи, выполняющиеся перед выключением приложения."""
        logger.info("Бот завершил работу")
        await self.bot.get_session()

    async def start_webhook(self, update: dict) -> None:
        """Передача события обработчикам."""
        telegram_update = types.Update(**update)
        await self.dp.process_update(telegram_update)

    def run(self) -> None:
        """Запуск локального сервера."""
        uvicorn.run(
            app=self.app,
            host=self.host,
            port=self.port,
        )
