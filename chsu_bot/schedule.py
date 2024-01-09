"""Модуль преобразования расписания в текст."""

import datetime


class Schedule:
    """Класс преобразования расписания в текст."""

    def __init__(self) -> None:
        self.week_days = {
            "Sunday": "воскресенье",
            "Monday": "понедельник",
            "Tuesday": "вторник",
            "Wednesday": "среда",
            "Thursday": "четверг",
            "Friday": "пятница",
            "Saturday": "суббота",
        }

    def render(self, unparse_schedule: list[dict[str, str]]) -> str:
        """Создание расписания в текстовом виде."""
        schedule = ""
        if unparse_schedule != []:
            for i in range(len(unparse_schedule)):
                if i == 0:
                    date = unparse_schedule[i]["dateEvent"]
                    schedule += (
                        f"*Расписание на {date} - "
                        f"{self.get_week_day(date)}*\n\n"
                    )
                schedule += self.get_duration_lesson(unparse_schedule[i])
                schedule += self.get_lesson_and_type(unparse_schedule[i])
                schedule += self.get_lecture(unparse_schedule[i])
                schedule += self.get_auditory(unparse_schedule[i])
            return schedule
        return "Расписание не найдено"

    @staticmethod
    def get_duration_lesson(lecture: dict[str, str]) -> str:
        """Получение времени занятия."""
        return f"⌚ {lecture['startTime']}-{lecture['endTime']}\n"

    @staticmethod
    def get_lesson_and_type(lecture: dict[str, str]) -> None:
        """Получение названия занятия и его типа."""
        if lecture["abbrlessontype"] is None:
            return f"🏫 {lecture['discipline']['title']}\n"
        return (
            f"🏫 {lecture['abbrlessontype']}. "
            f"{lecture['discipline']['title']}\n"
        )

    @staticmethod
    def get_lecture(lecture: dict[str, str]) -> str:
        """Получение преподавателей."""
        lecturers = []
        for lecturer in lecture["lecturers"]:
            lecturers.append(lecturer["shortName"])

        return f"🧑 {', '.join(lecturers)}\n"

    @staticmethod
    def get_auditory(lecture: dict[str, str]) -> str:
        """Получение номера аудитории."""
        if lecture["onlineEvent"] is not None:
            return "🏢 Онлайн\n\n"
        elif lecture["auditory"] is None:
            return "🏢 -/-\n\n"
        elif lecture["build"] is None:
            return f"🏢 {lecture['auditory']['title']}"
        return (
            f"🏢 {lecture['auditory']['title']}, "
            f"{lecture['build']['title'].lower()}\n\n"
        )

    def get_week_day(self, date: str) -> str:
        """Получение названия дня недели на русском."""
        day, month, year = map(int, date.split("."))
        return self.week_days[
            datetime.date(year=year, month=month, day=day).strftime("%A")
        ]
