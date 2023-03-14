"""Модуль для записи данных пользователя в БД."""

from typing import List, Optional

import aiosqlite
from database.group_db import get_group_id


async def check_user_id(user_id: int) -> bool:
    """Проверка пользователя на его наличие в БД."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM users WHERE userId=?", [user_id]
            )
            if await cursor.fetchone() is None:
                return False
            else:
                return True


async def add_user_id(user_id: int, group_name: Optional[int] = 0) -> None:
    """Добавление id пользователя в БД."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO users (userId, groupId) VALUES (?, ?)",
                [user_id, group_name],
            )
            await db.commit()


async def change_user_group(user_id: int, group: Optional[str] = None) -> None:
    """Смена группы пользователя в БД."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            if group is None:
                group_id = 0
            else:
                group_id = await get_group_id(group)
            await cursor.execute(
                f"UPDATE users SET groupId={group_id} WHERE userId={user_id}"
            )
            await db.commit()


async def get_users_id() -> List[int]:
    """Получение id всех пользователей бота."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT userId FROM users"
            )
            return [user_id[0] for user_id in await cursor.fetchall()]


async def check_user_group(user_id: int) -> bool:
    """Проверка наличия группы пользователя в БД."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT groupId FROM users WHERE userId=?", [user_id]
            )
            if (await cursor.fetchone())[0] == 0:
                return False
            else:
                return True


async def get_user_group(user_id: int) -> int:
    """Получение группы пользователя."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT groupId FROM users WHERE userId=?", [user_id]
            )
            return (await cursor.fetchone())[0]
