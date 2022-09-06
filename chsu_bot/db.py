from typing import List, Tuple
import aiosqlite


async def create_table() -> None:
    async with aiosqlite.connect("chsuBot.db") as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS groupId (
            groupName TEXT,
            id INTEGER
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
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("DELETE FROM groupId;",)
            for elem in ids_and_group_names:
                await cursor.execute("INSERT INTO groupId (groupName, id) VALUES (?, ?)", [elem["title"], elem["id"]])
                await db.commit()


async def get_group_id(group_name: str) -> int:
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT id FROM groupId WHERE groupName=?", [group_name])
            return (await cursor.fetchone())[0]


async def check_group_name(group_name: str) -> bool:
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT * FROM groupId WHERE groupName=?", [group_name])
            if await cursor.fetchone() is None:
                return False
            else:
                return True


async def get_group_names():
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT groupName FROM groupID")
            return await cursor.fetchall()


async def check_user_group_name(user_id: int) -> bool:
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT groupId FROM users WHERE userId=?", [user_id])
            if (await cursor.fetchone())[0] == 0:
                return False
            else:
                return True


async def check_user_id(user_id: int) -> bool:
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT * FROM users WHERE userId=?", [user_id])
            if await cursor.fetchone() is None:
                return False
            else:
                return True


async def add_user_id(user_id: int, group_name=0) -> None:
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("INSERT INTO users (userId, groupId) VALUES (?, ?)", [user_id, group_name])
            await db.commit()


async def check_user_group(user_id: int) -> bool:
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT groupId FROM users WHERE userId=?", [user_id])
            if (await cursor.fetchone())[0] == 0:
                return False
            else:
                return True


async def change_user_group(user_id: int, group: str | int) -> None:
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            if group == 0:
                group_id = group
            else:
                group_id = await get_group_id(group)
            await cursor.execute(f"UPDATE users SET groupId={group_id} WHERE userId={user_id}")
            await db.commit()


async def get_user_group(user_id: int) -> int:
    async with aiosqlite.connect("chsuBot.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT groupId FROM users WHERE userId=?", [user_id])
            return (await cursor.fetchone())[0]
