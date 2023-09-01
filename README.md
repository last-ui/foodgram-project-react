![workflow](https://github.com/last-ui/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)


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

**2. В контейнере backend выполнить миграции, создать суперпользователя и
собрать статику:**
```shell
docker-compose exec backend python manage.py migrate

docker-compose exec backend python manage.py createsuperuser

docker-compose exec backend python manage.py collectstatic --no-input
```

**3. Для наполнения базы данных из файла дампа fixtures.json:**

```shell
docker-compose exec backend python manage.py loaddata fixtures.json
```


<h2>Техническая документация</h2>

Для того чтобы получить, описанные понятным языком эндпоинты и настройки, да ещё с примерами запросов, да ещё с образцами ответов! Читай ReDoc, документация в этом формате доступна по ссылке:

http://host_adress/swagger/


<h2>Используемые технологии</h2>

- [Python 3.7](https://www.python.org/downloads/release/python-37/)
- [Django 3.2.3](https://www.djangoproject.com/download/)
- [Django Rest Framework 3.12.4](https://www.django-rest-framework.org/)
- [PostgreSQL 13.0](https://www.postgresql.org/download/)
- [gunicorn 20.0.4](https://pypi.org/project/gunicorn/)
- [nginx 1.19.3](https://nginx.org/ru/download.html)
- [Docker 20.10.14](https://www.docker.com/)
- [Docker Compose 2.4.1](https://docs.docker.com/compose/)
