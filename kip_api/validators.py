import os
from django.core.exceptions import ValidationError


def validate_image(image):
    ext = os.path.splitext(image.name)[1]
    valid_extensions = ['.jpg', '.png', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('тип файла не поддерживается.')