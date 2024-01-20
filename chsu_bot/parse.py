"""Модуль получения расписания ЧГУ."""

import datetime

import aiohttp


class ChsuAPI:
    """Класс получения расписания ЧГУ."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.url = "http://api.chsu.ru/api/"
        self.headers = {"user-agent": "88005553535"}
        self.token_headers = self.headers.copy()
        self.data = {"username": "mobil", "password": "ds3m#2nn"}
        self.session = session

    async def update_token(self) -> None:
        """Обновление токена в загаловках."""
        async with self.session.post(
            url=self.url + "auth/signin/",
            headers=self.token_headers,
            json=self.data,
        ) as resp:
            self.headers[
                "Authorization"
            ] = f"""Bearer {
                (await resp.json())["data"]
            }"""

    async def get_groups_ids(self) -> list[dict[str, int]]:
        """Получение списка всех групп."""
        while True:
            async with self.session.get(
                url=self.url + "group/v1",
                allow_redirects=False,
                headers=self.headers,
            ) as resp:
                try:
                    return await resp.json()
                except aiohttp.ContentTypeError:
                    if resp.status != 302:
                        return None
                    await self.update_token()

    async def get_schedule(
        self, group_id: int, start_date: str, end_date: str = None
    ) -> list[dict]:
        """Получение расписания для конкретной группы."""
        body_request = (
            f"timetable/v1/from/{start_date}/"
            f"to/{end_date or start_date}/groupId/{group_id}/"
        )
        link = self.url + body_request
        while True:
            async with self.session.get(
                url=link, allow_redirects=False, headers=self.headers
            ) as resp:
                try:
                    return await resp.json()
                except aiohttp.ContentTypeError:
                    if resp.status != 302:
                        return None
                    await self.update_token()

    async def get_all_groups_schedule(self) -> list[dict[str, str]]:
        """Получение расписания для всех групп на ближайшие два дня."""
        today = datetime.datetime.now()
        tomorrow = today + datetime.timedelta(days=1)
        body_request = "timetable/v1/event/from/{}/to/{}/".format(
            today.strftime("%d.%m.%Y"),
            tomorrow.strftime("%d.%m.%Y"),
        )
        while True:
            async with self.session.get(
                url=self.url + body_request,
                allow_redirects=False,
                headers=self.headers,
            ) as resp:
                try:
                    return await resp.json()
                except aiohttp.ContentTypeError:
                    if resp.status != 302:
                        return None
                    await self.update_token()
