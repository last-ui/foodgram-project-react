
<h1 align="center"> Проект: сайт Foodgram, «Продуктовый помощник» </h1>

___
<h4>Автор:</h4>

**Сластухин Александр** - студент Яндекс.Практикума Когорта 17+
https://github.com/last-ui

<h2>Краткое описание проекта</h2>

Онлайн-сервис и API для него. На этом сервисе пользователи
смогут публиковать рецепты, подписываться на публикации других
пользователей, добавлять понравившиеся рецепты в список «Избранное»,
а перед походом в магазин скачивать сводный список продуктов, необходимых
для приготовления одного или нескольких выбранных блюд.

<h2>Подготовка проекта к запуску</h2>

Заполнить .env-файл в разделе /infra/, вариант заполнения указан 
example.env.


<h2>Запуск проекта</h2>

**1. Из директории /infra/ запустить docker-compose командой:**
```shell
docker-compose up
```

или для пересборки
```shell
docker-compose up -d --build
```

**2. В контейнере web выполнить миграции, создать суперпользователя и 
собрать статику:**
```shell
docker-compose exec web python manage.py migrate

docker-compose exec web python manage.py createsuperuser

docker-compose exec web python manage.py collectstatic --no-input
```

**3. Для наполнения базы данных из файла дампа fixtures.json:**

```shell
docker-compose exec web python manage.py loaddata fixtures.json
```


<h2>Техническая документация</h2>

Для того чтобы получить, описанные понятным языком эндпоинты и настройки, да ещё с примерами запросов, да ещё с образцами ответов! Читай ReDoc, документация в этом формате доступна по ссылке:

http://127.0.0.1/api/docs/


<h2>Используемые технологии</h2>

Django==3.2.3
djangorestframework==3.12.4
djoser==2.1.0
webcolors==1.11.1
Pillow==9.0.0
python-dotenv==0.21.0
reportlab==3.6.12
psycopg2-binary==2.8.6
gunicorn==20.0.4