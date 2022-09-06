import datetime
from typing import List


async def render(json_response: List[dict]) -> str:
    if json_response != []:
        start_date = json_response[0]["dateEvent"]
        string_schedule = f"Расписание на {start_date}\n\n"
        for elem in json_response:
            date = elem["dateEvent"]
            if date != start_date:
                start_date = date
                string_schedule += f"Расписание на {date}\n\n"
            duration = f"{elem['startTime']}-{elem['endTime']}"
            lesson_name = f"{elem['abbrlessontype']}. {elem['discipline']['title']}"
            if elem["onlineEvent"] is None:
                auditory = f"{elem['auditory']['title']}, {elem['build']['title'].lower()}"
            else:
                auditory = "Онлайн"
            lecture = ", ".join([lecture["shortName"] for lecture in elem["lecturers"]])
            string_schedule += f"⌚ {duration}\n🏫 {lesson_name}\n🧑 {lecture}\n🏢 {auditory}\n\n"

        return string_schedule
    else:
        return "Расписание не найдено"


async def date_is_valid(date: str) -> bool:
    for elem in date:
        try:
            datetime.datetime.strptime(elem, "%d.%m.%Y")
        except ValueError:
            return False
    return True