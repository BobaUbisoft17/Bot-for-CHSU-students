"""Модуль шаблонов ответов пользователям."""

USER_GREETING = (
    "Здравствуйте, {message.from_user.first_name}!!!\n"
    "Я бот, упрощающий получение расписания занятий ЧГУ"
)

ADMIN_GREETING = (
    "Здравствуйте, {message.from_user.first_name}!!!\n"
    "Я бот, упрощающий получение расписания занятий ЧГУ"
    "\nПохоже вы аднимистратор!!!"
)

CHOICE_POST_TYPE = "Выберите тип поста"

GET_POST_TEXT = "Введите текст для поста"

GET_POST_PHOTO = "Отправьте мне фото для поста"

ALL_USERS_HAVE_BEEN_ANNOUNCED = "Все пользователи оповещены"

CHOICE_DATE = "Выберите, на какую дату хотите получить расписание"

GET_GROUP_NAME = "Введите название группы"

WRONG_GROUP_NAME = "Такой группы нет.\nПроверьте введённые данные"

DONT_BREAK_ME = "Не ломайте меня, пожалуйста🙏"

RANGE_LENGTH_EXCEEDED = (
    "Вы ввели слишком большой диапазон. "
    "Максимальная длина диапазона "
    "не должна превышать 31 дня. "
    "(Выберите другой день на клавиатуре)"
)

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

SERVER_NOT_ANSWER = (
    "Проблемы с сервером ЧГУ\n"
    "Повторите запрос, пожалуйста"
)
