"""Модуль для утилит."""

import datetime
from typing import Dict, List, Tuple


days_of_week = {
    "Sunday": "воскресенье",
    "Monday": "понедельник",
    "Tuesday": "вторник",
    "Wednesday": "среда",
    "Thursday": "четверг",
    "Friday": "пятница",
    "Saturday": "суббота",
}


def read_json(json: List[Dict[str, str]]) -> Dict[str, str]:
    """Чтение json и рендер расписания."""
    schedule = {}
    for elem in json:
        date = elem["dateEvent"]
        title = f"*Расписание на {date} - {get_week_day(date)}*"
        duration = get_duration_lesson(elem)
        lesson_name = get_lesson_and_type(elem)
        auditory = get_auditory(elem)
        lecture = get_lecture(elem)
        try:
            schedule[date] += (
                f"⌚ {duration}\n🏫 "
                f"{lesson_name}\n🧑 "
                f"{lecture}\n🏢 "
                f"{auditory}\n\n"
            )
        except KeyError:
            schedule[date] = (
                f"{title}\n\n⌚ "
                f"{duration}\n🏫 "
                f"{lesson_name}\n🧑 "
                f"{lecture}\n🏢 "
                f"{auditory}\n\n"
            )
    return schedule


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
    return ", ".join([lecture["shortName"] for lecture in json["lecturers"]])


def build_schedule(schedule: Dict[str, str]) -> List[str]:
    """Сборка расписания по строкам."""
    messages = []
    message = ""
    if "0" in schedule.keys():
        return [schedule["0"]]
    for lessons in schedule.values():
        if len(message + lessons) < 4096:
            message += lessons
        else:
            messages.append(message)
            message = lessons
    messages.append(message)
    return messages


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


def get_two_days_schedule(schedules: Dict[str, str]) -> Tuple[str, str]:
    """Подготовка расписания для передачи в БД."""
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
        "%d.%m.%Y"
    )
    if "0" in schedules.keys():
        return [schedules["0"]] * 2
    if len(schedules) == 2:
        return [schedules[today], schedules[tomorrow]]
    elif len(schedules) == 1 and today in schedules.keys():
        return [schedules[today], "Расписание не найдено"]
    return ["Расписание не найдено", schedules[tomorrow]]
