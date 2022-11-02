"""Модуль для работы с БД."""

from typing import Dict, List, Optional, Tuple
import aiosqlite
from utils import parse_dict


async def create_table() -> None:
    """Создание базы данных и таблиц в ней."""
    async with aiosqlite.connect("chsuBot.db") as db:
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


async def add_groups_ids(ids_and_group_names: List[Tuple[int, str]]) -> None:
    """Добавление групп в базу данных."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM groupId;",
            )
            for elem in ids_and_group_names:
                await cursor.execute(
                    "INSERT INTO groupId (groupName, id) VALUES (?, ?)",
                    [elem["title"], elem["id"]],
                )
                await db.commit()


async def update_group_schedule(
    schedules: Dict[str, str], group_id: int
) -> None:
    """Внесение расписания на два дня для переданной группы."""
    td_schedule, tm_schedule = parse_dict(schedules)
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "UPDATE groupId SET td_schedule=?, tm_schedule=? WHERE id=?",
                [td_schedule, tm_schedule, group_id],
            )
            await db.commit()


async def get_td_schedule(group_id: int) -> str:
    """Получение расписания на сегодня для переданной группы."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT td_schedule FROM groupId WHERE id=?", [group_id]
            )
            return (await cursor.fetchone())[0]


async def get_tm_schedule(group_id: int) -> str:
    """Получение расписания на завтра для переданной группы."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT tm_schedule FROM groupId WHERE id=?", [group_id]
            )
            return (await cursor.fetchone())[0]


async def get_group_ids() -> List[int]:
    """Получение id всех групп."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT id FROM groupId")
            return [group_id[0] for group_id in await cursor.fetchall()]


async def get_group_id(group_name: str) -> int:
    """Получение id группы."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT id FROM groupId WHERE groupName=?", [group_name]
            )
            return (await cursor.fetchone())[0]


async def check_group_name(group_name: str) -> bool:
    """Проверка имени группы на наличие в БД."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM groupId WHERE groupName=?", [group_name]
            )
            if await cursor.fetchone() is None:
                return False
            else:
                return True


async def get_group_names() -> List[str]:
    """Получение названия групп."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT groupName FROM groupID")
            return [group_name[0] for group_name in await cursor.fetchall()]


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


async def get_user_group(user_id: int) -> int:
    """Получение группы пользователя."""
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT groupId FROM users WHERE userId=?", [user_id]
            )
            return (await cursor.fetchone())[0]