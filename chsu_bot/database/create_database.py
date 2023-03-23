"""Модуль для работы с БД."""

import aiosqlite


async def create_table() -> None:
    """Создание базы данных и таблиц в ней."""
    async with aiosqlite.connect("./chsuBot.db") as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS groupId (
            groupName TEXT,
            id INTEGER,
            td_schedule TEXT,
            tm_schedule TEXT
        )"""
        )
        await db.commit()

        await db.execute(
            """CREATE TABLE IF NOT EXISTS users (
                userId INTEGER,
                groupId INTEGER
        )"""
        )
        await db.commit()
