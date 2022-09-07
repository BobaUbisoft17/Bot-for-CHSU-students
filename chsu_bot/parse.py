from typing import List
import aiohttp
from utils import render


URL = "http://api.chsu.ru/api/"
HEADERS = {}
data = {
    "username": "mobil",
    "password": "ds3m#2nn"
}

async def set_token() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.post(url=URL + "/auth/signin", json=data) as resp:
            HEADERS["Authorization"] = f'''Bearer {(await resp.json())["data"]}'''


async def get_groups_ids():
    await set_token()
    async with aiohttp.ClientSession() as session:
        async with session.get(url=URL + "group/v1", headers=HEADERS) as resp:
            return await resp.json()


async def get_schedule(group_id: int, start_date: str, end_date=None) -> List[dict]:
    body_request = f"timetable/v1/from/{start_date}/to/{end_date or start_date}/groupId/{group_id}/"
    await set_token()
    async with aiohttp.ClientSession() as session:
        async with session.get(url=URL+body_request, headers=HEADERS) as resp:
            return render(await resp.json())
