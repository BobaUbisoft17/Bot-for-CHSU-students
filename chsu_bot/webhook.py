"""Модуль для настройки webhook."""

import asyncio
import ssl

from aiohttp import web
import aiogram
from aiogram import types
from aiogram.dispatcher.webhook import get_new_configured_app
from aiogram.utils.executor import start_webhook
from fastapi import FastAPI
from logger import logger
import uvicorn


# class Webhook:
#     """Класс для управления вебхуком."""
# 
#     def __init__(
#         self,
#         dp: aiogram.Dispatcher,
#         bot: aiogram.Bot,
#         tasks: list,
#         webhook_path: str,
#         webhook_host: str,
#         host: str,
#         port: int,
#     ) -> None:
#         self.app = FastAPI()
#         self.webhook_host = webhook_host
#         self.webhook_path = webhook_path
#         self.webhook_url = self.webhook_host + self.webhook_path
#         self.host = host
#         self.port = port
#         self.dp = dp
#         self.bot = bot
#         self.tasks = tasks
# 
#         self.app.add_event_handler("startup", self.on_startup)
#         self.app.add_event_handler("shutdown", self.on_shutdown)
# 
#         self.app.add_api_route(
#             self.webhook_url, endpoint=self.start_webhook, methods=["POST"]
#         )
# 
#     async def on_startup(self) -> None:
#         """Задачи, выполняющиеся перед запуском приложения."""
#         webhook_info = await self.bot.get_webhook_info()
#         if webhook_info.url != self.webhook_url:
#             await self.bot.set_webhook(url=self.webhook_url)
#         for task in self.tasks:
#             asyncio.create_task(task)
# 
#         logger.info("Запуск бота")
# 
#     async def on_shutdown(self) -> None:
#         """Задачи, выполняющиеся перед выключением приложения."""
#         logger.info("Бот завершил работу")
#         await self.bot.get_session()
# 
#     async def start_webhook(self, update: dict) -> None:
#         """Передача события обработчикам."""
#         telegram_update = types.Update(**update)
#         await self.dp.process_update(telegram_update)
# 
#     def run(self) -> None:
#         """Запуск локального сервера."""
#         uvicorn.run(
#             app=self.app,
#             host=self.host,
#             port=self.port,
#         )

class Webhook:
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
        self.certificate = f"/etc/certs/live/{webhook_host}/fullchain.pem"
        self.privkey = f"/etc/certs/live/{webhook_host}/privkey.pem"
        self.WEBHOOK_URL = f"https://{webhook_host}:443{webhook_path}"
        self.WEBHOOK_PATH = webhook_path
        self.APP_HOST = host
        self.APP_PORT = port
        self.dp = dp
        self.bot = bot
        self.tasks = tasks

    async def on_startup(self, app) -> None:
        webhook = await self.bot.get_webhook_info()


        if webhook.url != self.WEBHOOK_URL:
            if not webhook.url:
                await self.bot.delete_webhook()

            await self.bot.set_webhook(self.WEBHOOK_URL, certificate=open(self.certificate, "rb"))

    async def on_shutdown(self, app) -> None:
        await self.bot.delete_webhook()

        await self.dp.storage.close()
        await self.dp.storage.wait_closed()

    async def run(self) -> None:
        app = get_new_configured_app(self.dp, self.WEBHOOK_PATH)

        app.on_startup.append(self.on_startup)
        app.on_shutdown.append(self.on_shutdown)

        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(self.certificate, self.privkey)

        loop = asyncio.get_event_loop()

        for task in self.tasks:
            loop.create_task(task)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(
            runner=runner,
            host=self.APP_HOST,
            port=self.APP_PORT,
            ssl_context=context,
        )
        await site.start()
        while True:
            await asyncio.sleep(3600)