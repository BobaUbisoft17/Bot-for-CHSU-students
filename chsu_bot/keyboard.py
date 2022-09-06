from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from db import get_group_names

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
    "Поддердать проект: 5536 9137 8142 8269"

)

back_button = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(text="Назад")
)


kb_greeting = (
    ReplyKeyboardMarkup(resize_keyboard=True)
    .add(KeyboardButton(text="Узнать расписание"))
    .add(KeyboardButton(text="Настройки"))
    .add(KeyboardButton(text="Помощь"))
)

kb_memory_group = (
    ReplyKeyboardMarkup(resize_keyboard=True)
    .add(KeyboardButton(text="Запомнить группу"))
    .add(KeyboardButton(text="Назад"))
)

kb_change_group = (
    ReplyKeyboardMarkup(resize_keyboard=True)
    .add(KeyboardButton(text="Изменить группу"))
    .add(KeyboardButton(text="Удалить данные о группе"))
    .add(KeyboardButton(text="Назад"))
)

kb_schedule = (
    ReplyKeyboardMarkup(resize_keyboard=True)
    .add(KeyboardButton(text="На сегодня"))
    .insert(KeyboardButton(text="На завтра"))
    .add(KeyboardButton(text="Выбрать другой день"))
    .add(KeyboardButton(text="Назад"))
)

async def create_kb_first_pt():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="Дальше »"))
    kb.add(KeyboardButton(text="Назад"))
    group_names = [group_name[0] for group_name in (await get_group_names())]
    for i in range((len(group_names) + 6) // 2):
        kb.add(KeyboardButton(text=group_names[i]))
    kb.add(KeyboardButton(text="Дальше »"))
    return kb

async def create_kb_second_pt():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="« Обратно"))
    kb.add(KeyboardButton(text="Назад"))
    group_names = [group_name[0] for group_name in (await get_group_names())]
    for i in range((len(group_names) + 6) // 2, len(group_names)):
        kb.add(KeyboardButton(text=group_names[i]))
    kb.add(KeyboardButton(text="« Обратно"))
    return kb