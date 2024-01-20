"""Модуль для настройки webhook."""

import asyncio

import aiogram
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web


class Webhook:
    """Класс для управления вебхуком."""

    def __init__(
        self,
        dp: aiogram.Dispatcher,
        bot: aiogram.Bot,
        webhook_path: str,
        webhook_host: str,
        host: str,
        port: int,
        tasks: list = None,
    ) -> None:
        self.WEBHOOK_URL = f"https://{webhook_host}:443{webhook_path}"
        self.WEBHOOK_PATH = webhook_path
        self.APP_HOST = host
        self.APP_PORT = port
        self.dp = dp
        self.bot = bot
        self.tasks = tasks

    async def on_startup(self, app: web.Application) -> None:
        """Установка вебхука."""
        webhook = await self.bot.get_webhook_info()

        if webhook.url != self.WEBHOOK_URL:
            if not webhook.url:
                await self.bot.delete_webhook()

            await self.bot.set_webhook(self.WEBHOOK_URL)

    async def on_shutdown(self, app: web.Application) -> None:
        """Удаление вебхука перед завершением работы приложения."""
        await self.bot.delete_webhook()

        await self.dp.storage.close()
        await self.dp.storage.wait_closed()

    async def run(self) -> None:
        """Запуск приложения."""
        # Получение настроенного aiogram приложения
        app = get_new_configured_app(self.dp, self.WEBHOOK_PATH)

        app.on_startup.append(self.on_startup)
        app.on_shutdown.append(self.on_shutdown)

        loop = asyncio.get_event_loop()

        # Добавление задач в цикл
        for task in self.tasks:
            loop.create_task(task)

        # асинхронный запуск aiohttp-сервера
        # способ используется под капотом web.run_app
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(
            runner=runner,
            host=self.APP_HOST,
            port=self.APP_PORT,
        )
        await site.start()
        while True:
            await asyncio.sleep(3600)
