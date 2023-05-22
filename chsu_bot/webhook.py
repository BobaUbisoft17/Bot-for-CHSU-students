"""Модуль для настройки webhook."""

import asyncio
import os

from aiogram import Bot, Dispatcher, types
from bot import bot, dp
from database.create_database import create_table
from database.group_db import add_groups_ids
from fastapi import FastAPI
from logger import logger
from parse import get_groups_ids
from update_schedule import loop_update_schedule, update_schedule


WEBHOOK_HOST = f"{os.getenv('DOMEN')}"
WEBHOOK_PATH = f"/bot/{os.getenv('BOTTOKEN')}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

Dispatcher.set_current(dp)
Bot.set_current(bot)

app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    """Задачи, выполняющиеся перед запуском приложения."""
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )
    logger.info("Запуск бота")
    await create_table()
    resp = await get_groups_ids()
    await add_groups_ids(resp)
    await update_schedule(0)
    asyncio.create_task(loop_update_schedule())


@app.post(WEBHOOK_PATH)
@logger.catch
async def bot_webhook(update: dict) -> None:
    """Передача события обработчикам."""
    telegram_update = types.Update(**update)
    await dp.process_update(telegram_update)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Задачи, выполняющиеся перед выключением приложения."""
    logger.info("Бот завершил работу")
    await bot.get_session()
