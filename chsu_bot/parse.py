"""Модуль для парсинга данных о расписании."""

from typing import Dict, List, Optional

import aiohttp
from utils import read_json


URL = "http://api.chsu.ru/api/"
HEADERS = {
    "user-agent": "88005553535"
}
data = {
    "username": "mobil",
    "password": "ds3m#2nn"
}


async def check_token() -> None:
    """Проверка валидности токена."""
    try:
        token = HEADERS["Authorization"]
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=URL + "auth/valid/",
                headers=HEADERS,
                data=token
            ) as resp:
                if await resp.text() == "false":
                    await set_token()
    except KeyError:
        await set_token()


async def set_token() -> None:
    """Получение и добавление токена в загаловки."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=URL + "auth/signin/",
            headers=HEADERS,
            json=data
        ) as resp:
            HEADERS["Authorization"] = f'''Bearer {
                (await resp.json())["data"]
            }'''


async def get_groups_ids() -> Dict[str, int]:
    """Получение списка всех групп."""
    await check_token()
    async with aiohttp.ClientSession() as session:
        async with session.get(url=URL + "group/v1", headers=HEADERS) as resp:
            return await resp.json()


async def get_schedule(
        group_id: int, start_date: str, end_date: Optional[str] = None
) -> List[dict]:
    """Получение и рендер расписания для конкретной группы."""
    body_request = (
        f"timetable/v1/from/{start_date}/"
        f"to/{end_date or start_date}/groupId/{group_id}/"
    )
    link = URL + body_request
    await check_token()
    async with aiohttp.ClientSession() as session:
        async with session.get(url=link, headers=HEADERS) as resp:
            if (await resp.json()) == []:
                return {"0" : "Расписание не найдено"}
            return read_json(await resp.json())
