import datetime
import logging

import asyncio
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text as TextFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageIsTooLong
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
    back_button,
    kb_greeting,
    kb_schedule,
    kb_change_group,
    kb_memory_group,
    create_kb_first_pt,
    create_kb_second_pt,
)
from utils import date_is_valid

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("BOTTOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())


class Get_schedule(StatesGroup):
    date = State()
    group = State()


class Memory_group(StatesGroup):
    group_name = State()


class Another_date(StatesGroup):
    date = State()
    group = State()


@dp.message_handler(commands="start")
async def send_welcome(message: types.Message):
    if not (await check_user_id(message.from_user.id)):
        await add_user_id(message.from_user.id)
    await message.answer(
        "Здравствуйте!!!\nЯ бот, упрощающий получение расписания занятий ЧГУ",
        reply_markup=kb_greeting,
    )


@dp.message_handler(TextFilter(equals="Узнать расписание"))
async def get_date(message: types.Message):
    if not await check_user_id(message.from_user.id):
        await add_user_id(message.from_user.id)
    await message.answer("Выберите дату", reply_markup=kb_schedule)


@dp.message_handler(TextFilter(equals=["На сегодня", "На завтра"]))
async def get_date(message: types.Message, state: FSMContext):
    if message.text == "На сегодня":
        date = datetime.datetime.now().strftime("%d.%m.%Y")
    else:
        date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
            "%d.%m.%Y"
        )

    if await check_user_group(message.from_user.id):
        group_id = await get_user_group(message.from_user.id)
        await message.answer(
            text=await get_schedule(
                group_id=group_id,
                start_date=date,
            ),
            reply_markup=kb_schedule,
        )
    else:
        async with state.proxy() as data:
            data["date"] = date

        await Get_schedule.group.set()
        await message.reply(
            "Введите название группы", reply_markup=(await create_kb_first_pt())
        )


@dp.message_handler(state=Get_schedule.group)
async def get_group(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.finish()
        await message.answer(text="Выберите дату", reply_markup=kb_schedule)
    elif message.text == "Дальше »":
        await message.answer(
            text="Меняем клавиатуру...",
            reply_markup=await create_kb_second_pt()
        )
    elif message.text == "« Обратно":
        await message.answer(
            text="Возвращаем клавиатуру...",
            reply_markup=await create_kb_first_pt()
        )
    elif await check_group_name(message.text):
        group_id = await get_group_id(message.text)
        async with state.proxy() as data:
            await message.answer(
                text=await get_schedule(group_id=group_id, start_date=data["date"]),
                reply_markup=kb_schedule,
            )
        await state.finish()
    else:
        await Get_schedule.group.set()
        await message.reply("Такой группы нет\nПроверьте введённые данные")


@dp.message_handler(TextFilter(equals="Настройки"))
async def settings(message: types.Message):
    if not await check_user_id(message.from_user.id):
        await add_user_id(message.from_user.id)
    if await check_user_group(message.from_user.id):
        keyboard = kb_change_group
    else:
        keyboard = kb_memory_group

    await message.answer(text="Переходим в раздел настроек", reply_markup=keyboard)


@dp.message_handler(TextFilter(equals="Запомнить группу"))
async def change_group(message: types.Message):
    if await check_user_group(message.from_user.id):
        await message.reply(text="Не ломайте меня, пожалуйста🙏")
    else:
        await Memory_group.group_name.set()
        await message.answer(
            "Введите название группы", reply_markup=(await create_kb_first_pt())
        )


@dp.message_handler(TextFilter(equals="Изменить группу"))
async def change_group(message: types.Message):
    if await check_user_group(message.from_user.id):
        await Memory_group.group_name.set()
        await message.answer(
            text="Введите название группы", reply_markup=(await create_kb_first_pt())
        )
    else:
        await message.reply(text="Не ломайте меня, пожалуйста🙏")


@dp.message_handler(state=Memory_group.group_name)
async def get_group_name(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.finish()
        await message.answer(
            text="Выберите дату",
            reply_markup=kb_greeting,
        )
    elif message.text == "Дальше »":
        await message.answer(
            text="Меняем клавиатуру...",
            reply_markup=await create_kb_second_pt()
        )
    elif message.text == "« Обратно":
        await message.answer(
            text="Возвращаем клавиатуру...",
            reply_markup=await create_kb_first_pt()
        )
    elif await check_group_name(message.text):
        if await get_user_group(message.from_user.id) != await get_group_id(message.text):
            await change_user_group(
                user_id=message.from_user.id,
                group=message.text
            )
            await state.finish()
            await message.answer(
                text="Я Вас запомнил\nТеперь вам не придёться выбирать группу",
                reply_markup=kb_greeting,
            )
        else:
            await Memory_group.group_name.set()
            await message.answer(
                text="Эта группа уже выбрана вами",
                reply_markup=await create_kb_first_pt()
            )
    else:
        await Memory_group.group_name.set()
        await message.reply("Такой группы нет\nПроверьте название и попробуйте ещё раз")


@dp.message_handler(TextFilter(equals="Удалить данные о группе"))
async def delete_user_group(message: types.Message):
    if await check_user_group(message.from_user.id):
        await change_user_group(user_id=message.from_user.id, group=0)
        await message.answer(
            text="Все данные о вашей группе удалены", reply_markup=kb_greeting
        )


@dp.message_handler(TextFilter(equals="Выбрать другой день"))
async def choice_another_day(message: types.Message):
    await Another_date.date.set()
    await message.answer(
        text=("Если вы хотите узнать дату на конкретный день, то введите дату согласно шаблону: "
              "20.06.2004\nЕсли вы хотите узнать на расписание на определённый период, "
              "то введите дату согласно шаблону: 20.06.2004-01.07.2022"),
        reply_markup=back_button,
    )

"""Переделать
   Выглядит очень плохо, как и работает
   Уже лучше, но нужно ещё лучше"""
@dp.message_handler(state=Another_date.date)
async def an_date(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.finish()
        await message.answer(
            text="Выберите дату",
            reply_markup=kb_schedule
        )
    elif await date_is_valid(message.text.split("-")):
        if len(message.text.split("-")) == 2:
            start_date, end_date = message.text.split("-")
        else:
            start_date, end_date = message.text, None
        if await check_user_group(message.from_user.id):
            group_id = await get_user_group(message.from_user.id)
            await state.finish()
            try:
                await message.answer(
                    text=await get_schedule(
                        group_id=group_id,
                        start_date=start_date,
                        end_date=end_date
                    ),
                    reply_markup=kb_schedule
                )
            except MessageIsTooLong:
                await Another_date.date.set()
                await message.answer(
                    text=("Вы ввели выбрали слишком большой диапазон" 
                          "Попробуйте ещё раз только с меньшим диапозоном"),
                    reply_markup=back_button
                )
        else:
            async with state.proxy() as data:
                data["start_date"], data["end_date"] = start_date, end_date
            await Another_date.next()
            await message.reply(
                text="Введите название вашей группы",
                reply_markup=await create_kb_first_pt()
            )
    else:
        await Another_date.date.set()
        await message.answer(
            text="Вы ввели некорректные данные",
            reply_markup=back_button
        )


@dp.message_handler(state=Another_date.group)
async def get_group(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.finish()
        await message.answer(
            text=("Если вы хотите узнать дату на конкретный день, то введите дату согласно шаблону: "
                  "20.06.2004\nЕсли вы хотите узнать на расписание на определённый период, "
                  "то введите дату согласно шаблону: 20.06.2004-01.07.2022"),
            reply_markup=back_button
        )
    elif message.text == "Дальше »":
        await message.answer(
            text="Меняем клавиатуру...",
            reply_markup=await create_kb_second_pt()
        )
    elif message.text == "« Обратно":
        await message.answer(
            text="Возвращаем клавиатуру...",
            reply_markup=await create_kb_first_pt()
        )
    elif await check_group_name(message.text):
        group_id = await get_group_id(message.text)
        async with state.proxy() as data:
            try:
                await message.answer(
                    text=await get_schedule(
                        group_id=group_id,
                        start_date=data["start_date"],
                        end_date=data["end_date"]
                    ),
                    reply_markup=kb_schedule
                )
            except MessageIsTooLong:
                await state.finish()
                await Another_date.date.set()
                await message.answer(
                    text=("Вы ввели выбрали слишком большой диапазон" 
                          "Попробуйте ещё раз только с меньшим диапозоном"),
                    reply_markup=back_button
                )
        await state.finish()
    else:
        await Another_date.group.set()
        await message.answer(
            text="Такой группы нет\nПопробуйте ещё раз",
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


def loop():
    loop = asyncio.get_event_loop_policy().get_event_loop()
    return loop


if __name__ == "__main__":
    loop().run_until_complete(create_table())
    resp = loop().run_until_complete(get_groups_ids())
    loop().run_until_complete(add_groups_ids(resp))
    executor.start_polling(dp, skip_updates=True)
