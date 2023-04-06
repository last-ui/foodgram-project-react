from django.core.exceptions import ValidationError

import webcolors


def webcolors_validate(data):
    try:
        return webcolors.hex_to_name(data)
    except ValueError:
        raise ValidationError('Для этого цвета нет имени')
