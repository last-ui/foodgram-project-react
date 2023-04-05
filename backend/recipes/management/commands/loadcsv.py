import csv
import os
import sys

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.transaction import atomic


class Command(BaseCommand):
    """
    Команда для извлечения данных из csv.
    Запуск:
    python manage.py loadcsv --filename ingredients --app recipe
     --model ingredient.
    """
    help = 'Создает данные из csv'

    def add_arguments(self, parser):
        parser.add_argument('--filename', type=str, help='filename')
        parser.add_argument('--app', type=str, help='app name')
        parser.add_argument('--model', type=str, help='model name to load')

    @atomic
    def handle(self, *args, **kwargs):
        file_name = kwargs['filename']
        app_label = kwargs['app']
        model_name = kwargs['model']
        file = os.path.join(settings.BASE_DIR, 'static', 'data',
                            f'{file_name}.csv')
        try:
            model = apps.get_model(app_label=app_label, model_name=model_name)
            model.objects.all().delete()
            with open(file, "r", encoding="utf-8-sig") as csv_file:
                data = csv.DictReader(csv_file, delimiter=",")
                model.objects.bulk_create(
                    model(**row) for row in data
                )
        except IOError:
            sys.exit(f"File with filename '{file_name}.csv' not found")
        except Exception as error:
            sys.exit(error)
