"""Модуль для утилит."""

import datetime
from typing import List


days_of_week = {
    "Sunday": "воскресенье",
    "Monday": "понедельник",
    "Tuesday": "вторник",
    "Wednesday": "среда",
    "Thursday": "четверг",
    "Friday": "пятница",
    "Saturday": "суббота",
}



def render(json_response: List[dict]) -> List[str]:
    """Рендер расписания."""
    if json_response != []:
        return read_json(json_response)
    else:
        return ["Расписание не найдено"]


def read_json(json: List[dict[str, str]]) -> List[str]:
    """Чтение json и рендер расписания."""
    schedule_messages = []
    message = ""
    schedule = ""
    for elem in json:
        date = elem["dateEvent"]
        if schedule == "":
            start_date = date
            schedule += f"*Расписание на {start_date} - {get_week_day(start_date)}*\n\n"
        elif date != start_date:
            start_date = date
            if len(message) + len(schedule) < 4096:
                message += schedule
            else:
                schedule_messages.append(message)
                message = schedule
            schedule = f"*Расписание на {start_date} - {get_week_day(start_date)}*\n\n"
        duration = f"{elem['startTime']}-{elem['endTime']}"
        if elem['abbrlessontype'] is None:
            lesson_name = f"{elem['discipline']['title']}"
        else:
            lesson_name = f"{elem['abbrlessontype']}. {elem['discipline']['title']}"
        if elem["onlineEvent"] != None:
            auditory = "Онлайн"
        elif elem["auditory"] is None:
            auditory = "-/-"
        else:
            auditory = f"{elem['auditory']['title']}, {elem['build']['title'].lower()}"
        lecture = ", ".join([lecture["shortName"] for lecture in elem["lecturers"]])
        schedule += f"⌚ {duration}\n🏫 {lesson_name}\n🧑 {lecture}\n🏢 {auditory}\n\n"
    if len(message) + len(schedule) < 4096:
        schedule_messages.append(message + schedule)
    else:
        schedule_messages.append(message)
        schedule_messages.append(schedule)
    return schedule_messages


def valid_range_length(start_date: str, end_date: str) -> bool:
    """Проверка временного диапазона на соответствие допустимой длине."""
    start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y")
    end_date = datetime.datetime.strptime(end_date, "%d.%m.%Y")
    return -31 <= (end_date - start_date).days <= 31


def valid_date(fst_date: str, snd_date: str) -> bool:
    fst_date = datetime.datetime.strptime(fst_date, "%d.%m.%Y")
    snd_date = datetime.datetime.strptime(snd_date, "%d.%m.%Y")
    return snd_date >= fst_date


def get_week_day(date: str):
    """Получение названия дня недели на русском."""
    day, month, year = map(int, date.split("."))
    return days_of_week[datetime.date(year=year, month=month, day=day).strftime("%A")]


def formated_date(date: str) -> str:
    """Форматирование даты к необходимой для запроса форме."""
    return datetime.datetime.strptime(date, "%d.%m.%Y").strftime("%d.%m.%Y")
