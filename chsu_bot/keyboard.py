"""Модуль для создания клавиатур."""

from calendar import monthrange
import datetime
from itertools import zip_longest
from typing import List

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from database.group_db import get_group_names

month_by_number = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}

days = [
    "Пн",
    "Вт",
    "Ср",
    "Чт",
    "Пт",
    "Сб",
    "Вс",
]

HELP = (
    "Бот, упрощающий получение расписания студениами ЧГУ.\n\n"
    "Получение расписания - можно получать расписание как на сегодня/завтра, "
    "так и на произвольную дату или произвольный промежуток."
    "Есть функция запоминания группы пользователя для получения "
    "расписания по нажатию *одной кнопки.\n\n"
    "Исходный код скоро будет выложен на GitHub "
    "https://github.com/BobaUbisoft17\n"
    "Связаться с автором проекта:\n"
    "Телеграм @BobaUbisoft\n"
    "VK vk.com/bobaubisoft\n"
    "Почта aksud2316@gmail.com\n\n"
    "Поддержать проект: 5536 9137 8142 8269"
)

empty_kb = ReplyKeyboardMarkup()


class BackButtonKeyboard(ReplyKeyboardMarkup):
    """Кнопка выхода в главное меню."""

    def __init__(self) -> None:
        super().__init__(keyboard=[
            KeyboardButton(text="Назад")
        ], resize_keyboard=True)


class GreetingKeyboard(ReplyKeyboardMarkup):
    """Основная клавиатура."""

    def __init__(self) -> None:
        super().__init__(keyboard=[
            [KeyboardButton(text="Узнать расписание")],
            [KeyboardButton(text="Настройки")],
            [KeyboardButton(text="Помощь")],
        ], resize_keyboard=True)


class AdminGreetingKeyboard(ReplyKeyboardMarkup):
    """Клавиатура для админа."""

    def __init__(self) -> None:
        super().__init__(keyboard=[
            [KeyboardButton(text="Узнать расписание")],
            [KeyboardButton(text="Настройки")],
            [KeyboardButton(text="Помощь")],
            [KeyboardButton(text="Сделать запись")],
        ], resize_keyboard=True)


class PostKeyboard(ReplyKeyboardMarkup):
    """Клавиатура для выбора типа записи."""

    def __init__(self) -> None:
        super().__init__(keyboard=[
            [KeyboardButton(text="Текстовый пост")],
            [KeyboardButton(text="Фото")],
            [KeyboardButton(text="Смешанный пост")],
            [KeyboardButton(text="Назад")],
        ], resize_keyboard=True)


class SettingsKeyboard(ReplyKeyboardMarkup):
    """Клавиатура выбора настроек."""

    def __init__(self) -> None:
        super().__init__(keyboard=[
            [KeyboardButton(text="Изменить данные о группе")],
            [KeyboardButton(text="Назад")],
        ], resize_keyboard=True)


class MemoryGroupKeyboard(ReplyKeyboardMarkup):
    """Клавиатруа запоминания группы."""

    def __init__(self) -> None:
        super().__init__(keyboard=[
            [KeyboardButton(text="Запомнить группу")],
            [KeyboardButton(text="Назад")]
        ], resize_keyboard=True)


class ChangeGroupKeyboard(ReplyKeyboardMarkup):
    """Клавиатура изменения данных о группе."""

    def __init__(self) -> None:
        super().__init__(keyboard=[
            [KeyboardButton(text="Изменить группу")],
            [KeyboardButton(text="Удалить данные о группе")],
            [KeyboardButton(text="Назад")],
        ], resize_keyboard=True)


class ChoiceDateKeyboard(ReplyKeyboardMarkup):
    """Клавиатура выбора даты."""

    def __init__(self) -> None:
        super().__init__(keyboard=[
            [
                KeyboardButton(text="На сегодня"),
                KeyboardButton(text="На завтра")],
            [
                KeyboardButton(text="Выбрать другой день"),
                KeyboardButton(text="Выбрать диапазон"),
            ],
            [KeyboardButton(text="Назад")],
        ], resize_keyboard=True)


async def first_pt_groups() -> ReplyKeyboardMarkup:
    """Создание клавиатуры для первой половины групп."""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="Дальше »"))
    kb.add(KeyboardButton(text="Назад"))
    group_names = await get_group_names()
    for i in range((len(group_names) + 6) // 2):
        kb.add(KeyboardButton(text=group_names[i]))
    kb.add(KeyboardButton(text="Дальше »"))
    return kb


async def second_pt_groups() -> ReplyKeyboardMarkup:
    """Создание клавиатуры для второй половины групп."""
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="« Обратно"))
    kb.add(KeyboardButton(text="Назад"))
    group_names = await get_group_names()
    for i in range((len(group_names) + 6) // 2, len(group_names)):
        kb.add(KeyboardButton(text=group_names[i]))
    kb.add(KeyboardButton(text="« Обратно"))
    return kb


class CalendarMarkup(InlineKeyboardMarkup):
    """Класс для создания календаря."""

    def __init__(self, month: int, year: int) -> None:
        """Инициализация всех значений."""
        self.month = month
        self.year = year
        super().__init__(inline_keyboard=[
            [self.title()],
            self.days_header(),
            *self.days(),
            self.nav_buttons()
        ])

    def next_month(self) -> 'CalendarMarkup':
        """Получение данных на следующий месяц."""
        current_month = datetime.date(self.year, self.month, 5)
        current_days_count = monthrange(self.year, self.month)[1]
        next_date = current_month + datetime.timedelta(days=current_days_count)
        return CalendarMarkup(next_date.month, next_date.year)

    def previous_month(self) -> 'CalendarMarkup':
        """Получение данных на предыдущий месяц."""
        current_month = datetime.date(self.year, self.month, 5)
        current_days_count = monthrange(self.year, self.month)[1]
        next_date = current_month - datetime.timedelta(days=current_days_count)
        return CalendarMarkup(next_date.month, next_date.year)

    def title(self) -> InlineKeyboardButton:
        """Создание заголовка календаря."""
        return InlineKeyboardButton(
            text=f"{month_by_number[self.month]} {self.year}",
            callback_data="None",
        )

    @staticmethod
    def days_header() -> List[InlineKeyboardButton]:
        """Добавление дней недели."""
        return [
            InlineKeyboardButton(text=day, callback_data="None")
            for day in days
        ]

    def days(self) -> List[List[InlineKeyboardButton]]:
        """Метод для заполнения календаря днями месяца."""
        start_day, days_count = monthrange(self.year, self.month)
        week_days = [
            InlineKeyboardButton(text=" ", callback_data="None")
        ] * start_day
        for i in range(1, days_count + 1):
            week_days.append(
                InlineKeyboardButton(
                    text=str(i),
                    callback_data=(
                        f"date {i:02}.{self.month:02}.{self.year:04}"
                    ),
                )
            )
        if len(week_days) % 7 != 0:
            week_days += [
                InlineKeyboardButton(text=" ", callback_data="None")
            ] * (7 - len(week_days) % 7)
        return list(zip_longest(*[iter(week_days)] * 7))

    def nav_buttons(self) -> List[InlineKeyboardButton]:
        """Добавление кнопок для перемещения по календарю."""
        return [
            InlineKeyboardButton(
                text="<", callback_data=f"back {self.month:02}.{self.year:04}"
            ),
            InlineKeyboardButton(text="Меню", callback_data="menu"),
            InlineKeyboardButton(
                text=">", callback_data=f"next {self.month:02}.{self.year:04}"
            ),
        ]
