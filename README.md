# Телеграм бот для получения расписания Череповецкого Государственного Универстита

Адрес бота: [@schedulechsubot](https://t.me/schedulechsubot)

## Возможности бота
+ Получение расписания на любой день
+ Запоминаие вашей группы
+ Получение расписания на выбранный временной диапазон
+ Ускоренное получение расписание на ближайшие два дня

## Использование

Начните диалог с ботом, перейдя по [ссылке](https://t.me/schedulechsubot)

Общение с ботом происходит за счёт использоваания клавиатур, которые он вам предоставит его использования

## Технологии

### Бот
+ Для взаимодействия с Telegram используется [aiogram](https://github.com/aiogram/aiogram)
+ Для логирования используется [loguru](https://github.com/Delgan/loguru)

### Получение расписания
+ Для отправки запросов к серверу ЧГУ используется [aiohttp](https://github.com/aio-libs/aiohttp)

### Получение переменных окружения 
+ Для получение переменных среды используетсяв [pydantic_settings](https://github.com/pydantic/pydantic-settings)

### Хранение данных пользователей(id-пользователя, id-группы)
+ В качестве базы данных используется [aiosqlite](https://github.com/omnilib/aiosqlite)

### Прокси сервер
+ Для проксирования запросов с домена на localhost используется [nginx](https://nginx.org/)

## Установка и запуск

Клонирование репозитория
~~~shell
git clone https://github.com/BobaUbisoft17/Bot-for-CHSU-students
~~~

### Добавление переменных среды

Необходимо создать файл .env, затем внести переменные среды([пример](https://github.com/BobaUbisoft17/Bot-for-CHSU-students/blob/main/env.sample))

### Конфигурация Nginx(если запуск производится на webhook)

Необходимо [файле конфигурации nginx](https://github.com/BobaUbisoft17/Bot-for-CHSU-students/blob/main/nginx-conf.d/app.conf) добавить доменное имя вашего сервера

~~~shell
server_name {Домен сервера/IP} => server_name example.com
~~~

### Запуск

#### Webhook
Необходимо первым запуском получить сертификат letsencrypt

~~~shell
docker-compose -f docker-compose-webhook.yml up --build
~~~

После получения сертификата нужно остановить контейнеры и зайти в [файл конфигурации nginx](https://github.com/BobaUbisoft17/Bot-for-CHSU-students/blob/main/nginx-conf.d/app.conf) и убрать все # этом файле. После выполнить команду

~~~shell
docker-compose -f docker-compose-webhook.yml up --build
~~~

После этих действий бот должен ожить

!!! В .env нужно указать HOST="0.0.0.0" иначе не получится проксировать запросы(особенности Docker)

#### Polling
Выполните команду:
~~~shell
docker-compose -f docker-compose-polling.yml --build
~~~
