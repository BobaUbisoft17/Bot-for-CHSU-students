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



def render(json_response: List[dict]) -> str:
    if json_response != []:
        start_date = json_response[0]["dateEvent"]
        string_schedule = f"Расписание на {start_date} - {get_week_day(start_date)}\n\n"
        for elem in json_response:
            date = elem["dateEvent"]
            if date != start_date:
                start_date = date
                string_schedule += f"Расписание на {date} - {get_week_day(start_date)}\n\n"
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


def date_is_valid(date: List[str]) -> bool:
    for elem in date:
        try:
            datetime.datetime.strptime(elem, "%d.%m.%Y")
        except ValueError:
            return False
    if len(date) == 2:
        start_date = datetime.datetime.strptime(date[0], "%d.%m.%Y")
        end_date = datetime.datetime.strptime(date[1], "%d.%m.%Y")
        return start_date <= end_date
    return True


def valid_range_length(start_date: str, end_date: str) -> bool:
    start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y")
    end_date = datetime.datetime.strptime(end_date, "%d.%m.%Y")
    return (end_date - start_date).days <= 31


def get_week_day(date: str):
    day, month, year = map(int, date.split("."))
    return days_of_week[datetime.date(year=year, month=month, day=day).strftime("%A")]
