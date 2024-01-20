"""Модуль для обработчиков бота."""

from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import (
    Command as CommandFilter,
    Text as TextFilter,
)
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, Update
from aiogram.utils import exceptions
from db import Groups, Users
import keyboard as kb
from loguru._logger import Logger
from parse import ChsuAPI
from router import CallbackRouter, ErrorRouter, MessageRouter, Routes
from schedule import Schedule
import templtaes as tmp


class BotLogic(Routes):
    """Класс для добавления обработчиков."""

    def __init__(
        self, logger: Logger, gs: Groups, us: Users, api: ChsuAPI
    ) -> None:
        super().__init__(
            Welcome(us),
            ChooseDate(us),
            TodaySchedule(api, gs, us),
            TomorrowSchedule(gs, us),
            GetAnotherDaySchedule(api, gs),
            GetRangeDateSchedule(api, us),
            GetSettings(us),
            RememberGroup(us),
            GetDate(api, us),
            GetInstitute(gs),
            GetGroup(api, gs, us),
            ChangeUserGroup(us),
            DeleteUserGroup(us),
            BackToMainMenu(),
            Help(),
            Errors(logger)
        )


class Welcome(MessageRouter):
    """Класс обработки команды /start."""

    def __init__(self, db: Users) -> None:
        self.db = db
        super().__init__(
            message_filters=CommandFilter("start"),
            handler=self.handle,
        )

    async def handle(self, message: Message) -> None:
        """Метод обработки сообщения."""
        if not (await self.db.in_db(message.from_user.id)):
            await self.db.add_user(message.from_user.id)
        await message.answer(
            text=tmp.USER_GREETING.format(message.from_user.first_name),
            reply_markup=kb.GreetingKeyboard(),
        )


class ChooseDate(MessageRouter):
    """Класс обработки сообщения 'Узнать расписание'."""

    def __init__(self, db: Users) -> None:
        self.db = db
        super().__init__(
            message_filters=TextFilter("Узнать расписание"),
            handler=self.handle,
        )

    async def handle(self, message: Message) -> None:
        """Метод обработки сообщения."""
        if not await self.db.in_db(message.from_user.id):
            await self.db.add_user(message.from_user.id)
        await message.answer(
            text=tmp.CHOICE_DATE,
            reply_markup=kb.ChoiceDateKeyboard(),
        )


class TodayScheduleSelection(StatesGroup):
    """Класс состояний для получения расписания на сегодня."""

    institute = State()
    group = State()


class TodaySchedule(MessageRouter):
    """Класс обработки сообщения 'На сегодня'."""

    def __init__(self, api: ChsuAPI, gs: Groups, us: Users) -> None:
        self.api = api
        self.us = us
        self.gs = gs
        super().__init__(
            message_filters=TextFilter("На сегодня"),
            handler=self.handle,
        )

    async def handle(self, message: Message, state: FSMContext) -> None:
        """Метод обработки сообщения."""
        if not await self.us.in_db(message.from_user.id):
            await self.us.add_user(message.from_user.id)
        if await self.us.has_group(message.from_user.id):
            group_id = await self.us.get_group(message.from_user.id)
            schedule = [await self.gs.td_schedule(group_id)]
            await state.finish()
            await ScheduleService(schedule, message).send_schedule()
        else:
            await state.set_state(TodayScheduleSelection.institute)
            await message.answer(
                text=tmp.CHOOSE_FIRST_INSTITUTE_NUMBER,
                reply_markup=kb.Institutions(),
            )


class TomorrowScheduleSelection(StatesGroup):
    """Класс состояний для получения расписания на завтра."""

    institute = State()
    group = State()


class TomorrowSchedule(MessageRouter):
    """Класс обработки сообщения 'На завтра'."""

    def __init__(self, gs: Groups, us: Users) -> None:
        self.us = us
        self.gs = gs
        super().__init__(
            message_filters=TextFilter("На завтра"),
            handler=self.handle,
        )

    async def handle(self, message: Message, state: FSMContext) -> None:
        """Метод обработки сообщения."""
        if not await self.us.in_db(message.from_user.id):
            await self.us.add_user(message.from_user.id)

        if await self.us.has_group(message.from_user.id):
            group_id = await self.us.get_group(message.from_user.id)
            schedule = [await self.gs.tm_schedule(group_id)]
            await state.finish()
            await ScheduleService(schedule, message).send_schedule()
        else:
            await state.set_state(TomorrowScheduleSelection.institute)
            await message.answer(
                text=tmp.CHOOSE_FIRST_INSTITUTE_NUMBER,
                reply_markup=kb.Institutions(),
            )


class ScheduleDateSelection(StatesGroup):
    """Класс состояний для получения расписания за определённую дату."""

    date = State()
    institute = State()
    group = State()


class GetAnotherDaySchedule(MessageRouter):
    """Класс обработки сообщения 'Выбрать другой день'."""

    def __init__(self, api: ChsuAPI, us: Users) -> None:
        self.api = api
        self.us = us
        super().__init__(
            message_filters=TextFilter("Выбрать другой день"),
            handler=self.handle,
        )

    async def handle(self, message: Message, state: FSMContext) -> None:
        """Метод обработки сообщения."""
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        await state.set_state(ScheduleDateSelection.date)
        await message.answer(
            text="Выберите день:",
            reply_markup=kb.CalendarMarkup(current_month, current_year),
        )


class ScheduleRangeSelection(StatesGroup):
    """Класс состояний для получения расписания за временной промежуток."""

    start = State()
    end = State()
    institute = State()
    group = State()


class GetRangeDateSchedule(MessageRouter):
    """Класс обработки сообщения 'Выбрать диапазон'."""

    def __init__(self, api: ChsuAPI, us: Users) -> None:
        self.api = api
        self.us = us
        super().__init__(
            message_filters=TextFilter("Выбрать диапазон"),
            handler=self.handle,
        )

    async def handle(self, message: Message, state: FSMContext) -> None:
        """Метод обработки сообщения."""
        await state.set_state(ScheduleRangeSelection.start)
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        await message.answer(
            text="Выберите первый день диапазона:",
            reply_markup=kb.CalendarMarkup(current_month, current_year),
        )


class GetDate(CallbackRouter):
    """Класс получения даты."""

    def __init__(self, api: ChsuAPI, us: Users) -> None:
        self.api = api
        self.us = us
        super().__init__(
            state=[
                ScheduleRangeSelection.start,
                ScheduleRangeSelection.end,
                ScheduleDateSelection.date,
            ],
            handler=self.handle,
        )

    async def handle(self, callback: CallbackQuery, state: FSMContext) -> None:
        """Метод обработки сообщения."""
        match callback.data.split():
            case pointer, date:
                await self.change_month(pointer, date, callback)
            case "menu", :
                await state.finish()
                await callback.message.edit_text(text="Вложение удалено")
            case "None", :
                pass
            case date, :
                current_state = (await state.get_state()).split(":")[1]
                if current_state in [
                    "start",
                    "date",
                ] or await self.valid_range_length(date, state):
                    await self.save_date(date, state)
                    await self.answer(callback, state)
                else:
                    await callback.message.answer(
                        text=tmp.RANGE_LENGTH_EXCEEDED,
                    )

    @staticmethod
    async def valid_range_length(current_date: str, state: FSMContext) -> bool:
        """Проверка валидности длины временного интервала."""
        data = await state.get_data()
        date = datetime.strptime(current_date, "%d.%m.%Y")
        return abs(date - data["start_date"]).days <= 31

    @staticmethod
    async def change_month(
        pointer: str, date: str, callback: CallbackQuery
    ) -> None:
        """Смена месяца на клваиатуре."""
        month, year = map(int, date.split("."))
        calendar = kb.CalendarMarkup(month, year)
        if pointer == "next":
            await callback.message.edit_reply_markup(calendar.next_month())
        else:
            await callback.message.edit_reply_markup(calendar.previous_month())

    async def save_date(self, date: str, state: FSMContext) -> None:
        """Сохранение выбранной даты."""
        date = datetime.strptime(date, "%d.%m.%Y")
        state_name, current_state = (await state.get_state()).split(":")
        if state_name == "ScheduleDateSelection":
            await state.update_data(start_date=date)
            await state.update_data(end_date=date)
        else:
            if current_state == "start":
                await state.update_data(start_date=date)
            else:
                date = await self.date_correction(date, state)
                await state.update_data(end_date=date)

    @staticmethod
    async def date_correction(current_date: str, state: FSMContext) -> str:
        """Приведение дат к неубывающему виду."""
        data = await state.get_data()
        if data["start_date"] > current_date:
            data["start_date"], current_date = current_date, data["start_date"]
            await state.update_data(start_date=data["start_date"])
            return current_date

        return current_date

    @staticmethod
    async def close_markup(callback: CallbackQuery) -> None:
        """Скрытие клавиатуры."""
        await callback.message.edit_text("Вложение удалено")

    async def answer(self, callback: CallbackQuery, state: FSMContext) -> None:
        """Ответ пользователю."""
        state_name, current_state = (await state.get_state()).split(":")
        if current_state == "date" or current_state == "end":
            if await self.us.has_group(callback.from_user.id):
                data = await state.get_data()
                await state.finish()
                await self.close_markup(callback)
                group_id = await self.us.get_group(callback.from_user.id)
                schedule = await self.api.get_schedule(
                    group_id,
                    data["start_date"].strftime("%d.%m.%Y"),
                    data["end_date"].strftime("%d.%m.%Y"),
                )
                await ScheduleService(
                    schedule, callback.message
                ).send_schedule()
            else:
                state_name = eval(state_name)
                await state.set_state(state_name.institute)
                await callback.message.edit_text(
                    text=tmp.CHOOSE_FIRST_INSTITUTE_NUMBER,
                    reply_markup=kb.Institutions(),
                )
        else:
            await state.set_state(ScheduleRangeSelection.end)
            await callback.message.answer(
                text=(
                    "Выберите последний день диапазона "
                    "(выберите день на клавиатуре сверху):"
                )
            )


class ChangeGroupInfo(StatesGroup):
    """Класс состояний для изменения группы пользователя."""

    institute = State()
    group = State()


class GetInstitute(CallbackRouter):
    """Класс получения института пользователя."""

    def __init__(self, gs: Groups) -> None:
        self.gs = gs
        super().__init__(
            state=[
                ChangeGroupInfo.institute,
                ScheduleDateSelection.institute,
                ScheduleRangeSelection.institute,
                TodayScheduleSelection.institute,
                TomorrowScheduleSelection.institute,
            ],
            handler=self.handle,
        )

    async def handle(self, callback: CallbackQuery, state: FSMContext) -> None:
        """Метод обработки сообщения."""
        match callback.data:
            case "back":
                await state.finish()
                await callback.message.edit_text("Вложение удалено")
            case institute:
                groups = await self.gs.get_groups_by_first_symbol(
                    callback.data
                )
                state_name = eval((await state.get_state()).split(":")[0])
                await state.set_state(state_name.group)
                await callback.message.edit_text(
                    text="Выберите вашу группу",
                    reply_markup=kb.GroupKeyboard(groups, institute, 1),
                )


class GetGroup(CallbackRouter):
    """Класс получения группы пользователя."""

    def __init__(self, api: ChsuAPI, gs: Groups, us: Users) -> None:
        self.api = api
        self.gs = gs
        self.us = us
        super().__init__(
            state=[
                ChangeGroupInfo.group,
                ScheduleDateSelection.group,
                ScheduleRangeSelection.group,
                TodayScheduleSelection.group,
                TomorrowScheduleSelection.group,
            ],
            handler=self.handle,
        )

    @staticmethod
    async def close_markup(callback: CallbackQuery) -> None:
        """Скрытие клавиатуры."""
        await callback.message.edit_text(text="Вложение удалено")

    async def handle(self, callback: CallbackQuery, state: FSMContext) -> None:
        """Метод обработки сообщения."""
        match callback.data.split():
            case "back", :
                state_name = eval((await state.get_state()).split(":")[0])
                await state.set_state(state_name.institute)
                await callback.message.edit_text(
                    text=tmp.CHOOSE_FIRST_INSTITUTE_NUMBER,
                    reply_markup=kb.Institutions(),
                )
            case "next" | "previous", institute, part:
                groups = await self.gs.get_groups_by_first_symbol(institute)
                await callback.message.edit_reply_markup(
                    kb.GroupKeyboard(groups, institute, int(part))
                )
            case group_id, :
                state_name = (await state.get_state()).split(":")[0]
                if state_name == "ChangeGroupInfo":
                    await self.change_group(int(group_id), callback, state)
                else:
                    await self.send_schedule(int(group_id), callback, state)

    async def send_schedule(
        self, group_id: int, callback: CallbackQuery, state: FSMContext
    ) -> None:
        """Отправка сообщения пользователю."""
        await self.close_markup(callback)
        state_info = await state.get_state()
        schedule = []
        match state_info.split(":"):
            case "TodayScheduleSelection", _:
                schedule = [await self.gs.td_schedule(group_id)]
            case "TomorrowScheduleSelection", _:
                schedule = [await self.gs.tm_schedule(group_id)]
            case "ScheduleDateSelection" | "ScheduleRangeSelection", _:
                data = await state.get_data()
                schedule = await self.api.get_schedule(
                    group_id,
                    data["start_date"].strftime("%d.%m.%Y"),
                    data["end_date"].strftime("%d.%m.%Y"),
                )

        await state.finish()
        await ScheduleService(schedule, callback.message).send_schedule()

    async def change_group(
        self, group_id: int, callback: CallbackQuery, state: FSMContext
    ) -> None:
        """Изменение группы пользователя."""
        if await self.us.get_group(callback.from_user.id) == group_id:
            await callback.answer("Эта группа уже выбрана вами")
        else:
            await self.close_markup(callback)
            await state.finish()
            await self.us.change_group(callback.from_user.id, group_id)
            await callback.message.answer(
                text="Информация о Вашей группе успешно изменена",
                reply_markup=kb.GreetingKeyboard(),
            )


class ScheduleService:
    """Класс отправки расписания пользователю."""

    def __init__(
        self, schedule: list[dict] | list[str], message: Message
    ) -> None:
        self.message = message
        self.schedule = self.build_schedule(schedule)

    @staticmethod
    def fined_double_breaks(schedule: str) -> list[int]:
        """Поиск индексов двойных переносов строк."""
        breakers = []
        for i in range(1, len(schedule)):
            if schedule[i - 1 : i + 1] == "\n\n" and schedule[i - 2] != "*":
                breakers.append(i)
        return breakers

    @staticmethod
    def sort_schedule_by_date(schedule: list[dict]) -> dict[str, list[dict]]:
        """Сортировка расписания по дате."""
        sorted_schedule = {}
        for lecture in schedule:
            date = lecture["dateEvent"]
            if sorted_schedule.get(date) is None:
                sorted_schedule[date] = []
            sorted_schedule[date].append(lecture)

        return sorted_schedule

    def build_schedule(
        self, unparse_schedule: list[dict] | list[str]
    ) -> list[str]:
        """Сборка сообщений с расписанием для отправки пользователю."""
        messages = []
        message = ""
        if len(unparse_schedule) == 0:
            return [Schedule().render(unparse_schedule)]

        if not isinstance(unparse_schedule[0], str):
            sorted_schedule = self.sort_schedule_by_date(
                unparse_schedule
            ).values()
        else:
            sorted_schedule = unparse_schedule
        for schedule in sorted_schedule:
            message = self.add_schedule(schedule, message, messages)
        if message != "":
            messages.append(message)
        return messages

    def add_schedule(
        self, schedule: list[str] | dict, message: str, messages: list[str]
    ) -> str:
        """Добавление расписания на день в список сообщений."""
        if isinstance(schedule, str):
            day_schedule = schedule
        else:
            day_schedule = Schedule().render(schedule)

        if len(message + day_schedule) < 4096:
            return message + day_schedule

        if len(day_schedule) >= 4096:
            double_breaks = self.fined_double_breaks(day_schedule)
            half = double_breaks[len(double_breaks) // 2]
            if len(message) != 0:
                messages.append(message)
            messages.append(day_schedule[:half])
            return day_schedule[half:]

        messages.append(message)
        return ""

    async def send_schedule(self) -> None:
        """Отправление расписания пользователю."""
        keyboard = None
        for i in range(len(self.schedule)):
            if i == len(self.schedule) - 1:
                keyboard = kb.ChoiceDateKeyboard()
            await self.message.answer(
                text=self.schedule[i],
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

        self.schedule.clear()


class GetSettings(MessageRouter):
    """Класс обработки сообщения 'Настройки'."""

    def __init__(self, us: Users) -> None:
        self.us = us
        super().__init__(
            message_filters=TextFilter("Настройки"),
            handler=self.handle,
        )

    async def handle(self, message: Message) -> None:
        """Метод обработки сообщения."""
        if await self.us.has_group(message.from_user.id):
            await message.answer(
                text="Переходим в раздел настроек",
                reply_markup=kb.ChangeGroupKeyboard(),
            )
        else:
            await message.answer(
                text="Переходим в раздел настроек",
                reply_markup=kb.MemoryGroupKeyboard(),
            )


class RememberGroup(MessageRouter):
    """Класс обработки сообщения 'Запомнить группу'."""

    def __init__(self, us: Users) -> None:
        self.us = us
        super().__init__(
            message_filters=TextFilter("Запомнить группу"),
            handler=self.handle,
        )

    async def handle(self, message: Message, state: FSMContext) -> None:
        """Метод обработки сообщения."""
        if await self.us.has_group(message.from_user.id):
            await message.answer(
                text=tmp.DONT_BREAK_ME,
            )
        else:
            await state.set_state(ChangeGroupInfo.institute)
            await message.answer(
                text=tmp.CHOOSE_FIRST_INSTITUTE_NUMBER,
                reply_markup=kb.Institutions(),
            )


class ChangeUserGroup(MessageRouter):
    """Класс обработки сообщения 'Изменить группу'."""

    def __init__(self, us: Users) -> None:
        self.us = us
        super().__init__(
            message_filters=TextFilter("Изменить группу"),
            handler=self.handle,
        )

    async def handle(self, message: Message, state: FSMContext) -> None:
        """Метод обработки сообщения."""
        if not await self.us.has_group(message.from_user.id):
            await message.answer(
                text=tmp.DONT_BREAK_ME,
            )
        else:
            await state.set_state(ChangeGroupInfo.institute)
            await message.answer(
                text=tmp.CHOOSE_FIRST_INSTITUTE_NUMBER,
                reply_markup=kb.Institutions(),
            )


class DeleteUserGroup(MessageRouter):
    """Класс обработки сообщения 'Удалить данные о группе'."""

    def __init__(self, us: Users) -> None:
        self.us = us
        super().__init__(
            message_filters=TextFilter("Удалить данные о группе"),
            handler=self.handle,
        )

    async def handle(self, message: Message) -> None:
        """Метод обработки сообщения."""
        if not await self.us.has_group(message.from_user.id):
            await message.answer(
                text=tmp.DONT_BREAK_ME,
            )
        else:
            await self.us.delete_group(message.from_user.id)
            await message.answer(
                text="Данные о вашей группе успешно удалены",
                reply_markup=kb.GreetingKeyboard(),
            )


class BackToMainMenu(MessageRouter):
    """Класс обработки сообщения 'Назад'."""

    def __init__(self) -> None:
        super().__init__(
            message_filters=TextFilter("Назад"),
            handler=self.handle,
        )

    async def handle(self, message: Message) -> None:
        """Метод обработки сообщения."""
        await message.answer(
            text="Возвращаемся в главное меню",
            reply_markup=kb.GreetingKeyboard(),
        )


class Help(MessageRouter):
    """Класс обработки сообщения 'Помощь'."""

    def __init__(self) -> None:
        super().__init__(
            message_filters=TextFilter("Помощь"), handler=self.handle
        )

    async def handle(self, message: Message) -> None:
        """Метод обработки сообщения."""
        await message.answer(text=tmp.HELP)


class Errors(ErrorRouter):
    """Обработка ошибок в работе бота."""

    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        super().__init__(message_filters=(lambda *_: True), handler=self.handle)

    async def handle(self, update: Update, error: exceptions) -> bool:
        """Метод обработки сообщения."""
        await update.message.answer("Произошла непредвиденная ошибка")
        self.logger.exception(error)
        return True
