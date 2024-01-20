"""Модуль запуска приложеня."""

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiohttp
import aiosqlite
from config import Config
from db import Groups, Users
from handler import BotLogic
from logger import logger
from parse import ChsuAPI
from polling import Polling
from schedule import Schedule
from update_schedule import Reloader
from webhook import Webhook


async def main() -> None:
    """Запуск приложения."""
    config = Config()
    bot = Bot(config.BOTTOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    async with aiohttp.ClientSession() as session, aiosqlite.connect(
        config.DBURL
    ) as db_session:
        groups_db = Groups(db_session)
        await groups_db.create_table()
        users_db = Users(db_session)
        await users_db.create_table()
        api = ChsuAPI(session)
        groups = [
            [int(elem["id"]), elem["title"]]
            for elem in await api.get_groups_ids()
        ]
        await groups_db.add_group_ids(groups)
        schedule = Schedule()
        reloader = Reloader(logger, api, schedule, groups_db)
        await reloader.reload_schedule()
        logic = BotLogic(logger, groups_db, users_db, api)
        logic.register(dp)
        tasks = [reloader.loop_update_schedule()]
        if config.RUNTYPE == "polling":
            await Polling(dp, tasks).run()
        else:
            await Webhook(
                dp=dp,
                bot=bot,
                tasks=tasks,
                webhook_path=f"/bot/{config.BOTTOKEN}",
                webhook_host=f"{config.DOMEN}",
                host=config.HOST,
                port=config.PORT,
            ).run()


if __name__ == "__main__":
    asyncio.run(main())
