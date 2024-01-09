"""Модуль для взаимодействия с БД."""

import aiosqlite


class Groups:
    """Класс для создания и управления таблицей групп."""

    def __init__(self, conn: aiosqlite.Connection) -> None:
        self.conn = conn

    async def create_table(self) -> None:
        """Создание таблицы для групп."""
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER,
                name TEXT,
                td_schedule TEXT,
                tm_schedule TEXT
            )
            """
        )
        await self.conn.commit()

    async def add_group_ids(
        self, ids_and_groupnames: list[tuple[int, str]]
    ) -> None:
        """Добавление групп в БД."""
        await self.conn.execute("DELETE FROM groups")
        await self.conn.executemany(
            """
            INSERT INTO groups (id, name) VALUES (?, ?)
            """,
            ids_and_groupnames,
        )
        await self.conn.commit()

    async def unused_id(self, used_ids: list[int]) -> list[int]:
        """Получение ID групп, расписания для которых не было найдено."""
        ids = {}
        unused_id = []
        for used_id in used_ids:
            ids[used_id] = ...

        async with self.conn.execute(
            """
            SELECT id FROM groups
            """
        ) as cursor:
            for group in await cursor.fetchall():
                if ids.get(group[0]) is None:
                    unused_id.append(group[0])

            return unused_id

    async def update_groups_schedule(
        self, schedules: list[tuple[str, str, int]]
    ) -> None:
        """Обновление расписания в БД."""
        await self.conn.executemany(
            """
            UPDATE groups SET td_schedule=?, tm_schedule=?
            WHERE id=?
            """,
            schedules,
        )

        await self.conn.commit()

    async def td_schedule(self, group_id: int) -> str:
        """Получение расписания на сегодня."""
        async with self.conn.execute(
            """
            SELECT td_schedule FROM groups
            WHERE id=?
            """,
            (group_id,),
        ) as cursor:
            return (await cursor.fetchone())[0]

    async def tm_schedule(self, group_id: int) -> str:
        """Получение расписания на завтра."""
        async with self.conn.execute(
            """
            SELECT tm_schedule FROM groups
            WHERE id=?
            """,
            (group_id,),
        ) as cursor:
            return (await cursor.fetchone())[0]

    async def get_groups_by_first_symbol(
        self, symbol: str
    ) -> list[tuple[int, str]]:
        """Получение групп, имена которых начинаются с переданного символа."""
        async with self.conn.execute(
            """
            SELECT name, id FROM groups
            WHERE name LIKE ?||'%'
            """,
            (symbol,),
        ) as cursor:
            return await cursor.fetchall()


class Users:
    """Класс для создания и управления таблицы пользователей."""

    def __init__(self, conn: aiosqlite.Connection) -> None:
        self.conn = conn

    async def create_table(self) -> None:
        """Создание таблицы users."""
        await self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER,
                groupId INTEGER
            )
            """
        )

        await self.conn.commit()

    async def in_db(self, user_id: int) -> bool:
        """Проверка наличия пользователя в БД."""
        async with self.conn.execute(
            """
            SELECT * FROM users
            WHERE id=?
            """,
            (user_id,),
        ) as cursor:
            user = await cursor.fetchone()
            if user is None:
                return False
            return True

    async def add_user(self, user_id: int) -> None:
        """Добавление пользователя в БД."""
        await self.conn.execute(
            """
            INSERT INTO users (id) VALUES (?)
            """,
            (user_id,),
        )

        await self.conn.commit()

    async def change_group(self, user_id: int, group_id: int) -> None:
        """Изменение группы пользователя."""
        await self.conn.execute(
            """
            UPDATE users SET groupId=?
            WHERE id=?
            """,
            (group_id, user_id),
        )

        await self.conn.commit()

    async def get_ids(self) -> list[int]:
        """Получение ID всех пользователей бота."""
        async with self.conn.execute(
            """
            SELECT id FROM users
            """
        ) as cursor:
            user_ids = await cursor.fetchall()
            return [user_id[0] for user_id in user_ids]

    async def has_group(self, user_id: int) -> bool:
        """Проверка наличия группы у пользователя."""
        async with self.conn.execute(
            """
            SELECT EXISTS (
                SELECT * FROM users
                WHERE id=? and groupId IS NOT NULL
            )
            """,
            (user_id,),
        ) as cursor:
            return (await cursor.fetchone())[0]

    async def get_group(self, user_id: int) -> int:
        """Получение группы пользователя."""
        async with self.conn.execute(
            """
            SELECT groupId FROM users
            WHERE id=?
            """,
            (user_id,),
        ) as cursor:
            return (await cursor.fetchone())[0]

    async def delete_group(self, user_id: int) -> None:
        """Удаление группы пользователя."""
        await self.conn.execute(
            """
            UPDATE users SET groupID=NULL
            WHERE id=?
            """,
            (user_id,),
        )
