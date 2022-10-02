"""Модуль для работы с Telegram."""

import datetime
import logging

import asyncio
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text as TextFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from db import (
    change_user_group,
    check_user_group,
    get_group_id,
    get_user_group,
    check_group_name,
    create_table,
    add_groups_ids,
    check_user_id,
    add_user_id,
)
from parse import get_schedule, get_groups_ids
from keyboard import (
    HELP,
    kb_greeting,
    kb_schedule,
    kb_change_group,
    kb_memory_group,
    first_pt_groups,
    second_pt_groups,
    CalendarMarkup
)
from utils import (
    valid_date,
    formated_date,
    valid_range_length
)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("BOTTOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())


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


@dp.message_handler(commands="start")
async def send_welcome(message: types.Message):
    """Приветствует пользователя и переводит в главное меню."""
    if not (await check_user_id(message.from_user.id)):
        await add_user_id(message.from_user.id)
    await message.answer(
        "Здравствуйте!!!\nЯ бот, упрощающий получение расписания занятий ЧГУ",
        reply_markup=kb_greeting,
    )


@dp.message_handler(TextFilter(equals="Узнать расписание"))
async def get_date(message: types.Message):
    """Переводит пользователя в меню выбора даты получения расписания."""
    if not await check_user_id(message.from_user.id):
        await add_user_id(message.from_user.id)
    await message.answer("Выберите дату", reply_markup=kb_schedule)


@dp.message_handler(TextFilter(equals=["На сегодня", "На завтра"]))
async def get_td_tm_schedule(message: types.Message, state: FSMContext):
    """Получение расписания на сегодня/завтра.
    
    Если группа пользователя есть в БД, выводит расписание.
    В ином случае запускает машину состояний и ждёт группу
    пользователя.
    """
    if message.text == "На сегодня":
        date = datetime.datetime.now().strftime("%d.%m.%Y")
    else:
        date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
            "%d.%m.%Y"
        )

    if await check_user_group(message.from_user.id):
        group_id = await get_user_group(message.from_user.id)
        schedule = (await get_schedule(group_id, date))[0]
        await message.answer(
            text=schedule,
            reply_markup=kb_schedule,
            parse_mode="Markdown"
        )
    else:
        async with state.proxy() as data:
            data["date"] = date

        await Get_schedule.group.set()
        await message.reply(
            "Введите название группы", reply_markup=(await first_pt_groups())
        )


@dp.message_handler(state=Get_schedule.group)
async def get_group(message: types.Message, state: FSMContext):
    """Получение группы пользователя.
    
    Если группа валидна, то возвращает расписание.
    Если используются другие кнопки на клавиатуре,
    то выплняет их.
    В ином случае перезапускает состояние.
    """
    if message.text == "Назад":
        await state.finish()
        await message.answer(text="Выберите дату", reply_markup=kb_schedule)
    elif message.text == "Дальше »":
        await message.answer(
            text="Меняем клавиатуру...",
            reply_markup=await second_pt_groups()
        )
    elif message.text == "« Обратно":
        await message.answer(
            text="Возвращаем клавиатуру...",
            reply_markup=await first_pt_groups()
        )
    elif await check_group_name(message.text):
        group_id = await get_group_id(message.text)
        async with state.proxy() as data:
            schedule = (
                await get_schedule(
                    group_id=group_id,
                    start_date=data["date"]
                    )
                )[0]
            await message.answer(
                text=schedule,
                reply_markup=kb_schedule,
                parse_mode="Markdown"
            )
        await state.finish()
    else:
        await Get_schedule.group.set()
        await message.reply("Такой группы нет.\nПроверьте введённые данные")


@dp.message_handler(TextFilter(equals="Настройки"))
async def settings(message: types.Message):
    """Переводит пользователя в меню настроек."""
    if not await check_user_id(message.from_user.id):
        await add_user_id(message.from_user.id)
    if await check_user_group(message.from_user.id):
        keyboard = kb_change_group
    else:
        keyboard = kb_memory_group

    await message.answer(text="Переходим в раздел настроек", reply_markup=keyboard)


@dp.message_handler(TextFilter(equals="Запомнить группу"))
async def change_group(message: types.Message):
    """Запускает состояние для запоминания группы."""
    if await check_user_group(message.from_user.id):
        await message.reply(text="Не ломайте меня, пожалуйста🙏")
    else:
        await Memory_group.group_name.set()
        await message.answer(
            "Введите название группы", reply_markup=(await first_pt_groups())
        )


@dp.message_handler(TextFilter(equals="Изменить группу"))
async def change_group(message: types.Message):
    """Изменение группы пользователя."""
    if await check_user_group(message.from_user.id):
        await Memory_group.group_name.set()
        await message.answer(
            text="Введите название группы", reply_markup=(await first_pt_groups())
        )
    else:
        await message.reply(text="Не ломайте меня, пожалуйста🙏")


@dp.message_handler(state=Memory_group.group_name)
async def get_group_name(message: types.Message, state: FSMContext):
    """Сосотояние для запоминания группы пользователя."""
    if message.text == "Назад":
        await state.finish()
        await message.answer(
            text="Выберите дату",
            reply_markup=kb_greeting,
        )
    elif message.text == "Дальше »":
        await message.answer(
            text="Меняем клавиатуру...",
            reply_markup=await second_pt_groups()
        )
    elif message.text == "« Обратно":
        await message.answer(
            text="Возвращаем клавиатуру...",
            reply_markup=await first_pt_groups()
        )
    elif await check_group_name(message.text):
        if await get_user_group(message.from_user.id) != await get_group_id(message.text):
            await change_user_group(
                user_id=message.from_user.id,
                group=message.text
            )
            await state.finish()
            await message.answer(
                text="Я Вас запомнил.\nТеперь вам не придёться выбирать группу",
                reply_markup=kb_greeting,
            )
        else:
            await Memory_group.group_name.set()
            await message.answer(
                text="Эта группа уже выбрана вами",
                reply_markup=await first_pt_groups()
            )
    else:
        await Memory_group.group_name.set()
        await message.reply("Такой группы нет.\nПроверьте название и попробуйте ещё раз")


@dp.message_handler(TextFilter(equals="Удалить данные о группе"))
async def delete_user_group(message: types.Message):
    """Удаление данных о группе пользователя."""
    if await check_user_group(message.from_user.id):
        await change_user_group(user_id=message.from_user.id, group=0)
        await message.answer(
            text="Все данные о вашей группе удалены", reply_markup=kb_greeting
        )


@dp.message_handler(TextFilter(equals="Выбрать другой день"))
async def choice_another_day(message: types.Message):
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


@dp.callback_query_handler(state=Another_day.date)
async def choose_another_day(callback: types.CallbackQuery, state: FSMContext):
    """Получение даты из календаря.
    
    Если группа пользователя в БД, возвращаем расписание.
    В ином случае: запоминаем дату и запускаем состояние
    для получения группы пользователя.
    """
    if "date" in callback.data:
        start_day = formated_date(callback.data.split()[1])
        if await check_user_group(callback.from_user.id):
            group_id = await get_user_group(callback.from_user.id)
            await state.finish()
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            schedule = (await get_schedule(group_id, start_day))[0]
            await callback.message.answer(text=schedule, reply_markup=kb_schedule, parse_mode="Markdown")
        else:
            async with state.proxy() as data:
                data["date"] = start_day
            await Another_day.next()
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            await callback.message.answer(
                text="Введите название вашей группы",
                reply_markup=await first_pt_groups()
            )
    elif "next" in callback.data or "back" in callback.data:
        await change_month(callback)


@dp.message_handler(state=Another_day.group)
async def choose_group(message: types.Message, state: FSMContext):
    """Получение группы пользователя."""
    if message.text == "Назад":
        await Another_day.date.set()
        await change_day(message)
    elif message.text == "Дальше »":
        await message.answer(
            text="Меняем клавиатуру...",
            reply_markup=await second_pt_groups()
        )
    elif message.text == "« Обратно":
        await message.answer(
            text="Возвращаем клавиатуру...",
            reply_markup=await first_pt_groups()
        )
    elif await check_group_name(message.text):
        group_id = await get_group_id(message.text)
        async with state.proxy() as data:
            schedule = (await get_schedule(group_id, data["date"]))[0]
            await message.answer(text=schedule, reply_markup=kb_schedule, parse_mode="Markdown")
        await state.finish()
    else:
        await Another_day.group.set()
        await message.answer(
            text="Такой группы нет.\nПопробуйте ещё раз",
        )


@dp.message_handler(TextFilter(equals="Выбрать диапозон"))
async def choose_range(message: types.Message):
    """Переводит пользователя в меню выбора диапазона."""
    await Another_range.start_date.set()
    current_date = datetime.datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    await message.answer(
        text="Выберите первый день диапазона:",
        reply_markup=CalendarMarkup(current_month, current_year).build.kb,
    )


@dp.callback_query_handler(state=Another_range.start_date)
async def choose_start_day(callback: types.CallbackQuery, state: FSMContext):
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


@dp.callback_query_handler(state=Another_range.end_date)
async def choose_end_day(callback: types.CallbackQuery, state: FSMContext):
    """Получение последнего дня диапазона."""
    if "date" in callback.data:
        end_date = formated_date(callback.data.split()[1])
        async with state.proxy() as data:
            if valid_range_length(data["start_date"], end_date):
                if not valid_date(data["start_date"], end_date):
                    data["start_date"], end_date = end_date, data["start_date"]
                if await check_user_group(callback.from_user.id):
                    group_id = await get_user_group(callback.from_user.id)
                    await bot.delete_message(callback.from_user.id, callback.message.message_id)
                    await state.finish()
                    schedules = await get_schedule(group_id, data["start_date"], end_date)
                    for i in range(len(schedules) - 1):
                        await callback.message.answer(text=schedules[i], parse_mode="Markdown")
                    await callback.message.answer(text=schedules[-1], reply_markup=kb_schedule, parse_mode="Markdown")
                else:
                    data["end_date"] = end_date
                    await Another_range.next()
                    await bot.delete_message(callback.from_user.id, callback.message.message_id)
                    await callback.message.answer(
                        text="Введите название вашей группы",
                        reply_markup=await first_pt_groups()
                    )
            else:
                await callback.message.answer(text=(
                    "Вы ввели слишком большой диапазон. "
                    "Максимальная длина диапазона "
                    "не должна превышать 31 дня. "
                    "(Выберите другой день на клавиатуре)")
                )
    elif "next" in callback.data or "back" in callback.data:
        await change_month(callback)


@dp.message_handler(state=Another_range.group)
async def choose_group(message: types.Message, state: FSMContext):
    """Получение группы пользователя."""
    if message.text == "Назад":
        await Another_range.end_date.set()
        await change_day(message)
    elif await check_group_name(message.text):
        group_id = await get_group_id(message.text)
        async with state.proxy() as data:
            schedules = await get_schedule(group_id, data["start_date"], data["end_date"])
            await state.finish()
            for i in range(len(schedules) - 1):
                await message.answer(text=schedules[i], parse_mode="Markdown")
            await message.answer(text=schedules[-1], reply_markup=kb_schedule, parse_mode="Markdown")
    elif message.text == "Дальше »":
        await message.answer(
            text="Меняем клавиатуру...",
            reply_markup=await second_pt_groups()
        )
    elif message.text == "« Обратно":
        await message.answer(
            text="Возвращаем клавиатуру...",
            reply_markup=await first_pt_groups()
        )
    else:
        await Another_range.group.set()
        await message.answer(
            text="Такой группы нет.\nПопробуйте ещё раз",
        )


@dp.message_handler(TextFilter(equals="Назад"))
async def back(message: types.Message):
    await message.answer(text="Возвращаемся в главное меню", reply_markup=kb_greeting)


@dp.message_handler(TextFilter(equals="Помощь"))
async def send_help(message: types.Message):
    await message.answer(
        text=HELP,
        reply_markup=kb_greeting
    )


async def change_month(callback: types.CallbackQuery):
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


async def change_day(message: types.Message):
    """Позволяет изменить последний день в диапазоне."""
    current_date = datetime.datetime.now()
    month = current_date.month
    year = current_date.year
    await message.answer(
        text="Выберите последний день диапазона",
        reply_markup=CalendarMarkup(month, year).build.kb
    )


def loop():
    """Создаёт цикл."""
    loop = asyncio.get_event_loop_policy().get_event_loop()
    return loop


def main():
    """Запускает бота."""
    loop().run_until_complete(create_table())
    resp = loop().run_until_complete(get_groups_ids())
    loop().run_until_complete(add_groups_ids(resp))
    executor.start_polling(dp, skip_updates=True)
