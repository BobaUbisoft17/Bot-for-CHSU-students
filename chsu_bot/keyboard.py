"""Модуль для создания клавиатур."""

from calendar import monthrange
import datetime
from itertools import zip_longest

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

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


class BackButtonKeyboard(ReplyKeyboardMarkup):
    """Кнопка выхода в главное меню."""

    def __init__(self) -> None:
        super().__init__(
            keyboard=[[KeyboardButton(text="Назад")]], resize_keyboard=True
        )


class GreetingKeyboard(ReplyKeyboardMarkup):
    """Основная клавиатура."""

    def __init__(self) -> None:
        super().__init__(
            keyboard=[
                [KeyboardButton(text="Узнать расписание")],
                [KeyboardButton(text="Настройки")],
                [KeyboardButton(text="Помощь")],
            ],
            resize_keyboard=True,
        )


class AdminGreetingKeyboard(ReplyKeyboardMarkup):
    """Клавиатура для админа."""

    def __init__(self) -> None:
        super().__init__(
            keyboard=[
                [KeyboardButton(text="Узнать расписание")],
                [KeyboardButton(text="Настройки")],
                [KeyboardButton(text="Помощь")],
                [KeyboardButton(text="Сделать запись")],
            ],
            resize_keyboard=True,
        )


class PostKeyboard(ReplyKeyboardMarkup):
    """Клавиатура для выбора типа записи."""

    def __init__(self) -> None:
        super().__init__(
            keyboard=[
                [KeyboardButton(text="Текстовый пост")],
                [KeyboardButton(text="Фото")],
                [KeyboardButton(text="Смешанный пост")],
                [KeyboardButton(text="Назад")],
            ],
            resize_keyboard=True,
        )


class SettingsKeyboard(ReplyKeyboardMarkup):
    """Клавиатура выбора настроек."""

    def __init__(self) -> None:
        super().__init__(
            keyboard=[
                [KeyboardButton(text="Изменить данные о группе")],
                [KeyboardButton(text="Назад")],
            ],
            resize_keyboard=True,
        )


class MemoryGroupKeyboard(ReplyKeyboardMarkup):
    """Клавиатруа запоминания группы."""

    def __init__(self) -> None:
        super().__init__(
            keyboard=[
                [KeyboardButton(text="Запомнить группу")],
                [KeyboardButton(text="Назад")],
            ],
            resize_keyboard=True,
        )


class ChangeGroupKeyboard(ReplyKeyboardMarkup):
    """Клавиатура изменения данных о группе."""

    def __init__(self) -> None:
        super().__init__(
            keyboard=[
                [KeyboardButton(text="Изменить группу")],
                [KeyboardButton(text="Удалить данные о группе")],
                [KeyboardButton(text="Назад")],
            ],
            resize_keyboard=True,
        )


class ChoiceDateKeyboard(ReplyKeyboardMarkup):
    """Клавиатура выбора даты."""

    def __init__(self) -> None:
        super().__init__(
            keyboard=[
                [
                    KeyboardButton(text="На сегодня"),
                    KeyboardButton(text="На завтра"),
                ],
                [
                    KeyboardButton(text="Выбрать другой день"),
                    KeyboardButton(text="Выбрать диапазон"),
                ],
                [KeyboardButton(text="Назад")],
            ],
            resize_keyboard=True,
        )


class CalendarMarkup(InlineKeyboardMarkup):
    """Класс для создания календаря."""

    def __init__(self, month: int, year: int) -> None:
        """Инициализация всех значений."""
        self.month = month
        self.year = year
        super().__init__(
            inline_keyboard=[
                [self.title()],
                self.days_header(),
                *self.days(),
                self.nav_buttons(),
            ]
        )

    def next_month(self) -> "CalendarMarkup":
        """Получение данных на следующий месяц."""
        current_month = datetime.date(self.year, self.month, 5)
        current_days_count = monthrange(self.year, self.month)[1]
        next_date = current_month + datetime.timedelta(days=current_days_count)
        return CalendarMarkup(next_date.month, next_date.year)

    def previous_month(self) -> "CalendarMarkup":
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
    def days_header() -> list[InlineKeyboardButton]:
        """Добавление дней недели."""
        return [
            InlineKeyboardButton(text=day, callback_data="None")
            for day in days
        ]

    def days(self) -> list[list[InlineKeyboardButton]]:
        """Метод для заполнения календаря днями месяца."""
        start_day, days_count = monthrange(self.year, self.month)
        week_days = [
            InlineKeyboardButton(text=" ", callback_data="None")
        ] * start_day
        for i in range(1, days_count + 1):
            week_days.append(
                InlineKeyboardButton(
                    text=str(i),
                    callback_data=(f"{i:02}.{self.month:02}.{self.year:04}"),
                )
            )
        if len(week_days) % 7 != 0:
            week_days += [
                InlineKeyboardButton(text=" ", callback_data="None")
            ] * (7 - len(week_days) % 7)
        return list(zip_longest(*[iter(week_days)] * 7))

    def nav_buttons(self) -> list[InlineKeyboardButton]:
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


class Institutions(InlineKeyboardMarkup):
    """Класс для создания клавиатуры институтов."""

    def __init__(self) -> None:
        super().__init__(
            inline_keyboard=[*self.institution_numbers(), self.back_button()]
        )

    @staticmethod
    def institution_numbers() -> list[list[InlineKeyboardButton]]:
        """Создание клавиатуры с номерами групп/институтов."""
        return [
            [
                InlineKeyboardButton(text="0", callback_data="0"),
                InlineKeyboardButton(text="1", callback_data="1"),
                InlineKeyboardButton(text="2", callback_data="2"),
            ],
            [
                InlineKeyboardButton(text="3", callback_data="3"),
                InlineKeyboardButton(text="4", callback_data="4"),
                InlineKeyboardButton(text="5", callback_data="5"),
            ],
            [
                InlineKeyboardButton(text="6", callback_data="6"),
                InlineKeyboardButton(text="7", callback_data="7"),
                InlineKeyboardButton(text="9", callback_data="9"),
            ],
        ]

    @staticmethod
    def back_button() -> list[InlineKeyboardButton]:
        """Создание кнопки 'Назад'."""
        return [InlineKeyboardButton(text="Назад", callback_data="back")]


class GroupKeyboard(InlineKeyboardMarkup):
    """Класс для создания клавиатуры групп."""

    def __init__(
        self, groups: list[tuple[int, str]], institute: str, part: int
    ) -> None:
        self.groups = groups
        self.institute = institute
        self.part = part
        self.back_button = InlineKeyboardButton(
            text="Назад", callback_data="back"
        )
        self.next_button = InlineKeyboardButton(
            text=">", callback_data=f"next {institute} {self.part + 1}"
        )
        self.previous_button = InlineKeyboardButton(
            text="<", callback_data=f"previous {institute} {self.part - 1}"
        )

        super().__init__(
            inline_keyboard=[*self.group_buttons(), self.nav_buttons()]
        )

    def group_buttons(self) -> list[list[InlineKeyboardButton]]:
        """Создание кнопок с названиями групп."""
        group_buttons = []
        start = (self.part - 1) * 18
        end = self.part * 18
        groups = self.groups[start:end]
        for i in range(0, len(groups) - 1, 2):
            group_buttons.append(
                [
                    InlineKeyboardButton(
                        text=groups[i][0], callback_data=groups[i][1]
                    ),
                    InlineKeyboardButton(
                        text=groups[i + 1][0], callback_data=groups[i + 1][1]
                    ),
                ]
            )
        if len(groups) % 2 != 0:
            group_buttons.append(
                [
                    InlineKeyboardButton(
                        text=groups[-1][0], callback_data=groups[-1][1]
                    )
                ]
            )
        return group_buttons

    def nav_buttons(self) -> list[InlineKeyboardButton]:
        """Создание кнопок навигации."""
        if len(self.groups) <= 18:
            return [self.back_button]
        elif self.part == 1:
            return [self.back_button, self.next_button]
        elif self.part * 18 >= len(self.groups):
            return [self.previous_button, self.back_button]
        return [self.previous_button, self.back_button, self.next_button]
