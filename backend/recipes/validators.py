import webcolors
from django.core.exceptions import ValidationError


def webcolors_validate(data):
    try:
        return webcolors.hex_to_name(data)
    except ValueError:
        raise ValidationError('Для этого цвета нет имени')
