import os

from django.core.exceptions import ValidationError


def validate_image(image):
    ext = os.path.splitext(image.name)[1]
    valid_extensions = ['.jpg', '.png', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('тип файла не поддерживается.')


def validate_content_type(content_type, correct_content_types):
    if not content_type.lower() in correct_content_types:
        raise ValidationError('неподдерживаемый тип заголовка Content-Type.')