import os
import sys

from django.utils.version import get_version

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

root_dir_content = os.listdir(BASE_DIR)

MANAGE_PATH = BASE_DIR
project_dir_content = os.listdir(MANAGE_PATH)
FILENAME = 'manage.py'

if FILENAME not in project_dir_content:
    assert False, (
        f'В директории `{BASE_DIR}` не найден файл `{FILENAME}`. '
        f'Убедитесь, что у вас верная структура проекта.'
    )

assert get_version() < '4.0.0', 'Пожалуйста, используйте версию Django < 4.0.0'

# pytest_plugins = [
#     'tests.fixtures.fixture_user',
# ]
