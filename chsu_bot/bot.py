"""Модуль для работы с Telegram."""

import asyncio
import datetime
import os
from typing import Union

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text as TextFilter, IDFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import exceptions
from db import (
    add_groups_ids,
    add_user_id,
    change_user_group,
    check_group_name,
    check_user_group,
    check_user_id,
    create_table,
    get_group_id,
    get_td_schedule,
    get_tm_schedule,
    get_user_group,
    get_users_id,
)
from keyboard import (
    CalendarMarkup,
    first_pt_groups,
    HELP,
    admin_greeting,
    back_button,
    kb_change_group,
    kb_greeting,
    kb_memory_group,
    kb_post,
    kb_schedule,
    second_pt_groups,
)
from logger import logger
from parse import get_groups_ids, get_schedule
from update_schedule import loop_update_schedule, update_schedule
from utils import build_schedule, formated_date, valid_date, valid_range_length

bot = Bot(token=os.getenv("BOTTOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())
admin = os.getenv("admin_id")


class Get_schedule(StatesGroup):
    """Класс для запоминания дня при выборе расписания на сегодня/завтра."""

    date = State()
    group = State()


class Memory_group(StatesGroup):
    """Класс для запоминания группы пользователя."""

    group_name = State()


class Another_day(StatesGroup):
    """Класс для запоминания дня при выборе расписания на 'другой день'."""

    date = State()
    group = State()


class Another_range(StatesGroup):
    """Класс для запоминания дат при выборе диапазона дат."""

    start_date = State()
    end_date = State()
    group = State()


class Textpost(StatesGroup):
    """Класс для состояния текстового поста."""

    text = State()


class Photopost(StatesGroup):
    """Класс для состояния поста с фото."""

    picture = State()


class Mixpost(StatesGroup):
    """Класс для состояния смешанного поста."""

    text = State()
    picture = State()


@dp.message_handler(commands="start")
async def send_welcome(message: types.Message) -> None:
    """Приветствует пользователя и переводит в главное меню."""
    if not (await check_user_id(message.from_user.id)):
        await add_user_id(message.from_user.id)
    if message.from_user.id != admin:
        await message.answer(
            "Здравствуйте!!!\nЯ бот, упрощающий получение расписания занятий ЧГУ",
            reply_markup=kb_greeting,
        )
        logger.info(f"{message.from_user.id} выполнил команду '/start'")
    else:
        await message.answer(
            (
                "Здравствуйте!!!\nЯ бот, упрощающий получение расписания занятий ЧГУ"
                "\nС повышением!!!"
            ),
            reply_markup=admin_greeting,
        )


@dp.message_handler(IDFilter(admin), TextFilter(equals="Сделать запись"))
async def make_post(message: types.Message) -> None:
    """Переход к меню администратора."""
    await message.answer(
        text="Выберите тип поста",
        reply_markup=kb_post,
    )


@dp.message_handler(
    IDFilter(admin),
    TextFilter(["Текстовый пост", "Фото", "Смешанный пост"]),
)
async def get_txt_post(message: types.Message) -> None:
    """Переход к созданию поста."""
    if message.text == "Текстовый пост":
        await Textpost.text.set()
        await message.answer(
            text="Введите сообщение",
            reply_markup=back_button,
        )
    elif message.text == "Фото":
        await Photopost.picture.set()
        await message.answer(
            text="Отправьте мне фото для поста",
            reply_markup=back_button,
        )
    elif message.text == "Смешанный пост":
        await Mixpost.text.set()
        await message.answer(
            text="Введите текст для поста",
            reply_markup=back_button,
        )


@dp.message_handler(state=Textpost.text)
async def message_post(message: types.Message, state: FSMContext) -> None:
    """Создание текстового поста."""
    await state.finish()
    for user_id in await get_users_id():
        await bot.send_message(user_id, message.text)
    await message.answer(
        text="Все пользователи оповещены",
        reply_markup=admin_greeting,
    )


@dp.message_handler(state=Photopost.picture, content_types=["photo"])
async def send_img(message: types.Message, state: FSMContext) -> None:
    """Создание графического поста."""
    await state.finish()
    for user_id in await get_users_id():
        await bot.send_photo(user_id, message.photo[-1].file_id)
    await message.answer(
        text="Все пользователи оповещены",
        reply_markup=admin_greeting,
    )


@dp.message_handler(state=Mixpost.text)
async def memory_text(message: types.Message, state: FSMContext) -> None:
    """Получение текста для смешанного поста."""
    if message.text == "Назад":
        await state.finish()
        await message.answer(
            text="выберите тип поста",
            reply_markup=kb_post,
        )
    else:
        async with state.proxy() as data:
            data["text"] = message.text
        await Mixpost.next()
        await message.answer(
            text="Отправьте мне фото для поста",
        )


@dp.message_handler(state=Mixpost.picture, content_types=["photo"])
async def memory_pic(message: types.Message, state: FSMContext) -> None:
    """Получение фото и рассылка готового поста."""
    photo_id = message.photo[-1].file_id

    async with state.proxy() as data:
        for user_id in await get_users_id():
            await bot.send_photo(
                user_id,
                photo_id,
                data["text"],
            )
    await state.finish()
    await message.answer(
        text="Все пользователи оповещены",
        reply_markup=admin_greeting,
    )


@dp.message_handler(TextFilter(equals="Узнать расписание"))
async def get_date(message: types.Message) -> None:
    """Переводит пользователя в меню выбора даты получения расписания."""
    if not await check_user_id(message.from_user.id):
        await add_user_id(message.from_user.id)
    await message.answer(
        "Выберите на какую дату хотите получить расписание",
        reply_markup=kb_schedule,
    )
    logger.info(f"{message.from_user.id} нажал на кнопку '{message.text}'")


@dp.message_handler(TextFilter(equals=["На сегодня", "На завтра"]))
async def get_td_tm_schedule(
    message: types.Message,
    state: FSMContext
) -> None:
    """Получение расписания на сегодня/завтра.

    Если группа пользователя есть в БД, выводит расписание.
    В ином случае запускает машину состояний и ждёт группу
    пользователя.
    """
    logger.info(f"{message.from_user.id} нажал на кнопку '{message.text}'")
    if await check_user_group(message.from_user.id):
        group_id = await get_user_group(message.from_user.id)
        if message.text == "На сегодня":
            schedule = await get_td_schedule(group_id)
        else:
            schedule = await get_tm_schedule(group_id)
        await message.answer(
            text=schedule,
            reply_markup=kb_schedule,
            parse_mode="Markdown"
        )
        logger.info(
            f"{message.from_user.id} "
            f"получил расписание {message.text} для группы {group_id}"
        )
    else:
        async with state.proxy() as data:
            data["date"] = message.text

        await Get_schedule.group.set()
        await message.reply(
            "Введите название группы", reply_markup=(await first_pt_groups())
        )


@dp.message_handler(state=Get_schedule.group)
async def get_group(message: types.Message, state: FSMContext) -> None:
    """Получение группы пользователя.

    Если группа валидна, то возвращает расписание.
    Если используются другие кнопки на клавиатуре,
    то выплняет их.
    В ином случае перезапускает состояние.
    """
    if message.text == "Назад":
        await state.finish()
        await message.answer(text="Выберите дату", reply_markup=kb_schedule)
        logger.info(f"{message.from_user.id} вышел из состояния выбора группы")
    elif message.text == "Дальше »":
        await message.answer(
            text="Меняем клавиатуру...", reply_markup=await second_pt_groups()
        )
    elif message.text == "« Обратно":
        await message.answer(
            text="Возвращаем клавиатуру...",
            reply_markup=await first_pt_groups(),
        )
    elif await check_group_name(message.text):
        group_id = await get_group_id(message.text)
        async with state.proxy() as data:
            if data["date"] == "На сегодня":
                schedule = await get_td_schedule(group_id)
            else:
                schedule = await get_tm_schedule(group_id)
            await message.answer(
                text=schedule, reply_markup=kb_schedule, parse_mode="Markdown"
            )
            logger.info(
                f"{message.from_user.id} "
                f"получил расписание {data['date']} для группы {group_id}"
            )
        await state.finish()
    else:
        await Get_schedule.group.set()
        await message.reply("Такой группы нет.\nПроверьте введённые данные")


@dp.message_handler(TextFilter(equals="Настройки"))
async def settings(message: types.Message) -> None:
    """Переводит пользователя в меню настроек."""
    if not await check_user_id(message.from_user.id):
        await add_user_id(message.from_user.id)
    if await check_user_group(message.from_user.id):
        keyboard = kb_change_group
    else:
        keyboard = kb_memory_group

    await message.answer(
        text="Переходим в раздел настроек", reply_markup=keyboard
    )
    logger.info(f"{message.from_user.id} перешёл в меню настроек")


@dp.message_handler(TextFilter(equals="Запомнить группу"))
async def memory_group(message: types.Message) -> None:
    """Запускает состояние для запоминания группы."""
    if await check_user_group(message.from_user.id):
        await message.reply(text="Не ломайте меня, пожалуйста🙏")
    else:
        await Memory_group.group_name.set()
        await message.answer(
            "Введите название группы", reply_markup=(await first_pt_groups())
        )
        logger.info(
            f"{message.from_user.id} входит в состояние запоминания группы"
        )


@dp.message_handler(TextFilter(equals="Изменить группу"))
async def change_group(message: types.Message) -> None:
    """Изменение группы пользователя."""
    if await check_user_group(message.from_user.id):
        await Memory_group.group_name.set()
        await message.answer(
            text="Введите название группы",
            reply_markup=(await first_pt_groups()),
        )
        logger.info(
            f"{message.from_user.id} входит в состояние запоминания группы"
        )
    else:
        await message.reply(text="Не ломайте меня, пожалуйста🙏")


@dp.message_handler(state=Memory_group.group_name)
async def get_group_name(message: types.Message, state: FSMContext) -> None:
    """Сосотояние для запоминания группы пользователя."""
    if message.text == "Назад":
        await state.finish()
        await message.answer(
            text="Возвращаемся в главное меню",
            reply_markup=kb_greeting,
        )
        logger.info(
            f"{message.from_user.id} отказался от запоминания его группы"
        )
    elif message.text == "Дальше »":
        await message.answer(
            text="Меняем клавиатуру...", reply_markup=await second_pt_groups()
        )
    elif message.text == "« Обратно":
        await message.answer(
            text="Возвращаем клавиатуру...",
            reply_markup=await first_pt_groups(),
        )
    elif await check_group_name(message.text):
        if await get_user_group(message.from_user.id) != await get_group_id(
            message.text
        ):
            await change_user_group(
                user_id=message.from_user.id, group=message.text
            )
            await state.finish()
            await message.answer(
                text=(
                    "Я Вас запомнил.\n"
                    "Теперь вам не придётся выбирать группу"
                ),
                reply_markup=kb_greeting,
            )
            logger.info(
                f"Группа {message.from_user.id} {message.text} теперь в БД"
            )
        else:
            await Memory_group.group_name.set()
            await message.answer(
                text="Эта группа уже выбрана вами",
                reply_markup=await first_pt_groups(),
            )
    else:
        await Memory_group.group_name.set()
        await message.reply(
            "Такой группы нет.\nПроверьте название и попробуйте ещё раз"
        )


@dp.message_handler(TextFilter(equals="Удалить данные о группе"))
async def delete_user_group(message: types.Message) -> None:
    """Удаление данных о группе пользователя."""
    if await check_user_group(message.from_user.id):
        await change_user_group(user_id=message.from_user.id)
        await message.answer(
            text="Все данные о вашей группе удалены", reply_markup=kb_greeting
        )
        logger.info(f"Группа {message.from_user.id} удалена из БД")
    else:
        await message.answer(text="Не ломайте меня, пожалуйста🙏")


@dp.message_handler(TextFilter(equals="Выбрать другой день"))
async def choice_another_day(message: types.Message) -> None:
    """Получение расписания на день, выбранный пользователем.

    Возвращает клавиатуру-календарь.
    """
    await Another_day.date.set()
    current_date = datetime.datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    await message.answer(
        text="Выберите день:",
        reply_markup=CalendarMarkup(current_month, current_year).build.kb,
    )
    logger.info(
        f"{message.from_user.id} нажал на кнопку 'Выбрать другой день'"
    )


@dp.callback_query_handler(state=Another_day.date)
async def choose_another_day(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Получение даты из календаря.

    Если группа пользователя в БД, возвращаем расписание.
    В ином случае: запоминаем дату и запускаем состояние
    для получения группы пользователя.
    """
    if "date" in callback.data:
        start_day = formated_date(callback.data.split()[1])
        if await check_user_group(callback.from_user.id):
            await state.finish()
            group_id = await get_user_group(callback.from_user.id)
            await bot.delete_message(
                callback.from_user.id, callback.message.message_id
            )
            schedule = build_schedule(
                await get_schedule(group_id, start_day)
            )[0]
            await callback.message.answer(
                text=schedule, reply_markup=kb_schedule, parse_mode="Markdown"
            )
            logger.info(
                f"{callback.from_user.id} "
                f"получил расписание на {start_day} для группы {group_id}"
            )
        else:
            async with state.proxy() as data:
                data["date"] = start_day
            await Another_day.next()
            await bot.delete_message(
                callback.from_user.id, callback.message.message_id
            )
            await callback.message.answer(
                text="Введите название вашей группы",
                reply_markup=await first_pt_groups(),
            )
            logger.info(f"{callback.from_user.id} переходит к выбору группы")
    elif "next" in callback.data or "back" in callback.data:
        await change_month(callback)
    elif "menu" in callback.data:
        await bot.delete_message(
            callback.from_user.id, callback.message.message_id
        )
        await state.finish()
        await callback.message.answer(
            text="Выберите на какую дату хотите получить расписание",
            reply_markup=kb_schedule,
        )
        logger.info(f"{callback.from_user.id} вернулся в главное меню")


@dp.message_handler(state=Another_day.group)
async def choose_group(message: types.Message, state: FSMContext) -> None:
    """Получение группы пользователя."""
    if message.text == "Назад":
        await Another_day.date.set()
        await change_day(message)
    elif message.text == "Дальше »":
        await message.answer(
            text="Меняем клавиатуру...", reply_markup=await second_pt_groups()
        )
    elif message.text == "« Обратно":
        await message.answer(
            text="Возвращаем клавиатуру...",
            reply_markup=await first_pt_groups(),
        )
    elif await check_group_name(message.text):
        group_id = await get_group_id(message.text)
        async with state.proxy() as data:
            schedule = build_schedule(
                await get_schedule(group_id, data["date"])
            )[0]
            await message.answer(
                text=schedule, reply_markup=kb_schedule, parse_mode="Markdown"
            )
            logger.info(
                f"{message.from_user.id} "
                f"получил расписание на {data['date']} для группы {group_id}"
            )
        await state.finish()
    else:
        await Another_day.group.set()
        await message.answer(
            text="Такой группы нет.\nПопробуйте ещё раз",
        )


@dp.message_handler(TextFilter(equals="Выбрать диапазон"))
async def choose_range(message: types.Message) -> None:
    """Переводит пользователя в меню выбора диапазона."""
    await Another_range.start_date.set()
    current_date = datetime.datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    await message.answer(
        text="Выберите первый день диапазона:",
        reply_markup=CalendarMarkup(current_month, current_year).build.kb,
    )
    logger.info(f"{message.from_user.id} переходит к выбору диапазона")


@dp.callback_query_handler(state=Another_range.start_date)
async def choose_start_day(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Получение первого дня диапазона."""
    if "date" in callback.data:
        start_date = formated_date(callback.data.split()[1])
        async with state.proxy() as data:
            data["start_date"] = start_date
        await Another_range.next()
        await callback.message.answer(
            text=(
                "Выберите последний день диапазона "
                "(выберите день на клавиатуре сверху):"
            )
        )
    elif "next" in callback.data or "back" in callback.data:
        await change_month(callback)
    elif "menu" in callback.data:
        await bot.delete_message(
            callback.from_user.id, callback.message.message_id
        )
        await state.finish()
        await callback.message.answer(
            text="Выберите на какую дату хотите получить расписание",
            reply_markup=kb_schedule,
        )
        logger.info(f"{callback.from_user.id} вернулся в главное меню")


@dp.callback_query_handler(state=Another_range.end_date)
async def choose_end_day(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Получение последнего дня диапазона."""
    if "date" in callback.data:
        end_date = formated_date(callback.data.split()[1])
        async with state.proxy() as data:
            if valid_range_length(data["start_date"], end_date):
                if not valid_date(data["start_date"], end_date):
                    data["start_date"], end_date = end_date, data["start_date"]
                if await check_user_group(callback.from_user.id):
                    group_id = await get_user_group(callback.from_user.id)
                    await bot.delete_message(
                        callback.from_user.id, callback.message.message_id
                    )
                    await send_range_schedule(
                        callback, group_id,
                        data["start_date"],
                        end_date
                    )
                    await state.finish()
                else:
                    data["end_date"] = end_date
                    await Another_range.next()
                    await bot.delete_message(
                        callback.from_user.id, callback.message.message_id
                    )
                    await callback.message.answer(
                        text="Введите название вашей группы",
                        reply_markup=await first_pt_groups(),
                    )
            else:
                await callback.message.answer(
                    text=(
                        "Вы ввели слишком большой диапазон. "
                        "Максимальная длина диапазона "
                        "не должна превышать 31 дня. "
                        "(Выберите другой день на клавиатуре)"
                    )
                )
    elif "next" in callback.data or "back" in callback.data:
        await change_month(callback)
    elif "menu" in callback.data:
        await bot.delete_message(
            callback.from_user.id, callback.message.message_id
        )
        await state.finish()
        await callback.message.answer(
            text="Выберите на какую дату хотите получить расписание",
            reply_markup=kb_schedule,
        )
        logger.info(f"{callback.from_user.id} вернулся в главное меню")


@dp.message_handler(state=Another_range.group)
async def choose_group_range(
    message: types.Message, state: FSMContext
) -> None:
    """Получение группы пользователя."""
    if message.text == "Назад":
        await Another_range.end_date.set()
        await change_day(message)
    elif await check_group_name(message.text):
        group_id = await get_group_id(message.text)
        async with state.proxy() as data:
            start_date, end_date = data["start_date"], data["end_date"]
            await state.finish()
        await send_range_schedule(message, group_id, start_date, end_date)
    elif message.text == "Дальше »":
        await message.answer(
            text="Меняем клавиатуру...", reply_markup=await second_pt_groups()
        )
    elif message.text == "« Обратно":
        await message.answer(
            text="Возвращаем клавиатуру...",
            reply_markup=await first_pt_groups(),
        )
    else:
        await Another_range.group.set()
        await message.answer(
            text="Такой группы нет.\nПопробуйте ещё раз",
        )


@dp.message_handler(TextFilter(equals="Назад"))
async def back(message: types.Message) -> None:
    """Возвращение пользователя в главное меню."""
    await message.answer(
        text="Возвращаемся в главное меню", reply_markup=kb_greeting
    )


@dp.message_handler(TextFilter(equals="Помощь"))
async def send_help(message: types.Message) -> None:
    """Отправление сообщения с помощью."""
    await message.answer(text=HELP, reply_markup=kb_greeting)


async def change_month(callback: types.CallbackQuery) -> None:
    """Смена месяца на клавиатуре-календаре."""
    month, year = map(int, callback.data.split()[1].split("."))
    calendar = CalendarMarkup(month, year)
    if "next" in callback.data:
        await callback.message.edit_reply_markup(
            reply_markup=calendar.next_month().kb
        )
    else:
        await callback.message.edit_reply_markup(
            reply_markup=calendar.previous_month().kb
        )


async def change_day(message: types.Message) -> None:
    """Позволяет изменить последний день в диапазоне."""
    current_date = datetime.datetime.now()
    month = current_date.month
    year = current_date.year
    await message.answer(
        text="Выберите последний день диапазона",
        reply_markup=CalendarMarkup(month, year).build.kb,
    )


async def send_range_schedule(
    message: Union[
        types.CallbackQuery,
        types.Message
    ],
    group_id: int,
    start_date: str,
    end_date: str
) -> None:
    user_id = message.from_user.id
    schedules = build_schedule(
        await get_schedule(
            group_id, start_date, end_date
        )
    )
    if type(message) == types.CallbackQuery:
        message = message.message
    for i in range(len(schedules) - 1):
        await message.answer(
            text=schedules[i], parse_mode="Markdown"
        )
    await message.answer(
        text=schedules[-1],
        reply_markup=kb_schedule,
        parse_mode="Markdown",
    )
    logger.info(
        f"{user_id} "
        f"получил расписание на диапазон "
        f"{start_date}-{end_date} "
        f"для группы {group_id}"
    )


def loop() -> asyncio.AbstractEventLoop:
    """Создаёт цикл."""
    return asyncio.get_event_loop_policy().get_event_loop()


@dp.errors_handler()
async def handle_errors(update: types.Update, error: exceptions) -> bool:
    """Обработка неожиданных ошибок."""
    logger.exception("Произошла непредвиденная ошибка!")
    return True


@logger.catch
def main() -> None:
    """Запускает бота."""
    logger.info("Запуск бота")
    loop().run_until_complete(create_table())
    resp = loop().run_until_complete(get_groups_ids())
    loop().run_until_complete(add_groups_ids(resp))
    loop().run_until_complete(update_schedule(0))
    executor.start_polling(
        dp,
        skip_updates=True,
        loop=loop().create_task(loop_update_schedule())
    )
