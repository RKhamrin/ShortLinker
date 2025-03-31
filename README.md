# Об этом API

## Структура проекта: 

.
├── docker
│   ├── app.sh
│   └── celery.sh
├── src
│   ├── alembic
│   │   ├── versions
│   │   │   └── [файлы версий]
│   │   ├── README
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── auth
│   │   ├── db.py
│   │   ├── schemas.py
│   │   └── users.py
│   ├── links
│   │   ├── models.py
│   │   ├── router.py
│   │   └── schemas.py
│   ├── tasks
│   │   ├── router.py
│   │   └── tasks.py
│   ├── init.py
│   ├── alembic.ini
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── Dockerfile
├── init.py
├── docker-compose.yml
└── requirements.txt

Данное API предназначено для сокращения ссылок на Интернет-страницы и переадресации, а также подсчета статистик. API состоит из следующих разделов:
1. База данных -- развернутое postgres хранилище из двух таблиц, связь с к которым осуществляется через alembic;
2. Бэкенд -- FastApi, дополнительно добавлена регистрация пользователей -- также через FastAPI. Подробнее о ручках:

Ручка | Функционал ручки | Параметры | Ответ функции
| --- | --- | --- | --- |
POST /links/shorten | создание короткой ссылки и занесение информации о ней в базу данных | user_id, long_link (сама ссылка), custom_alias (кастомная короткая ссылка, должна быть размером 10), expires at (время истечения ссылки) | статус, короткая ссылка
GET /links/{short_code} | перенаправление на оригинальный URL | short_code (короткая ссылка) | Redirect, код 301
DELETE /links/{short_code} | удаление короткой ссылки и любой информации о ней | short_code (короткая ссылка) | статус
PUT /links/{short_code} | изменение короткой ссылки | short_code (короткая ссылка) | статус, новая короткая ссылка
GET /links/search?original_url={url} | получение длинной ссылки | url (короткая ссылка) | статус, длинная ссылка 

3. Кэширование важных эндпоинтов с помощью FastApi
4. Бэкграунд таски с помощью Celery и Redis для удаления короткой ссылки по истечению времени 
5. Разворачивание на сервере с помощью Docker

# Инструкция по запуску 

Шаги: 
1. Установка PgAdmin4 и установка postgres через brew (Mac), создание сервера
2. Создание файла .env со следующими параметрами: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
3. Установка Docker и корректировка docker-compose.yml
4. Поднятие контейнера (Postgres, Redis, Celery, FastApi и Flower поднимутся сами)
5. Готово! 

# Описание базы данных
    
Всего в базе данных 2 таблицы: User и Linking. В таблице User присутствуют следующие поля: id, user_id, email, hashed_password, registered_at, is_active, is_superuser, is_verified. Содержание таблицы Linking: user_id, long_link, custom_alias, expires_at, last_usage, creation_date, number_of_usages, is_authorized.
