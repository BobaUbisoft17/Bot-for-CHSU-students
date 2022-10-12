"""Модуль для утилит."""

import datetime
from typing import Dict, List


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


def read_json(json: List[Dict[str, str]]) -> List[str]:
    """Чтение json и рендер расписания."""
    schedule_messages = []
    message = ""
    schedule = ""
    for elem in json:
        date = elem["dateEvent"]
        if schedule == "":
            start_date = date
            schedule += (
                f"*Расписание на {start_date} *"
                f"*- {get_week_day(start_date)}*\n\n"
            )
        elif date != start_date:
            start_date = date
            if len(message) + len(schedule) < 4096:
                message += schedule
            else:
                schedule_messages.append(message)
                message = schedule
            schedule = (
                f"*Расписание на {start_date} *"
                f"*- {get_week_day(start_date)}*\n\n"
            )
        duration = get_duration_lesson(elem)
        lesson_name = get_lesson_and_type(elem)
        auditory = get_auditory(elem)
        lecture = get_lecture(elem)
        schedule += (
            f"⌚ {duration}\n🏫 {lesson_name}\n🧑 {lecture}\n🏢 {auditory}\n\n"
        )
    if len(message) + len(schedule) < 4096:
        schedule_messages.append(message + schedule)
    else:
        schedule_messages.append(message)
        schedule_messages.append(schedule)
    return schedule_messages


def get_duration_lesson(json: Dict[str, str]) -> str:
    """Получение времени занятия."""
    return f"{json['startTime']}-{json['endTime']}"


def get_lesson_and_type(json: Dict[str, str]) -> str:
    """Получение названия занятия и его типа."""
    if json["abbrlessontype"] is None:
        return f"{json['discipline']['title']}"
    return f"{json['abbrlessontype']}. {json['discipline']['title']}"


def get_auditory(json: Dict[str, str]) -> str:
    """Получение номера аудитории."""
    if json["onlineEvent"] is not None:
        return "Онлайн"
    elif json["auditory"] is None:
        return "-/-"
    return f"{json['auditory']['title']}, {json['build']['title'].lower()}"


def get_lecture(json: Dict[str, str]) -> str:
    """Получение преподавателей."""
    return ", ".join(
        [
            lecture["shortName"]
            for lecture in json["lecturers"]
        ]
    )


def valid_range_length(start_date: str, end_date: str) -> bool:
    """Проверка временного диапазона на соответствие допустимой длине."""
    start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y")
    end_date = datetime.datetime.strptime(end_date, "%d.%m.%Y")
    return -31 <= (end_date - start_date).days <= 31


def valid_date(fst_date: str, snd_date: str) -> bool:
    """Проверка действительности дат."""
    fst_date = datetime.datetime.strptime(fst_date, "%d.%m.%Y")
    snd_date = datetime.datetime.strptime(snd_date, "%d.%m.%Y")
    return snd_date >= fst_date


def get_week_day(date: str) -> str:
    """Получение названия дня недели на русском."""
    day, month, year = map(int, date.split("."))
    return days_of_week[
        datetime.date(year=year, month=month, day=day).strftime("%A")
    ]


def formated_date(date: str) -> str:
    """Форматирование даты к необходимой для запроса форме."""
    return datetime.datetime.strptime(date, "%d.%m.%Y").strftime("%d.%m.%Y")
