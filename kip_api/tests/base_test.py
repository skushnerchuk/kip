from django.test import TestCase
from django.db import models


class BaseTest(TestCase):
    """
    Базовый класс тестов
    """

    @staticmethod
    def field_exist(model, field):
        """Проверяем наличие поля field в модели model"""
        try:
            model.objects.get(id=1)._meta.get_field(field)
            return True
        except models.FieldDoesNotExist:
            return False

    def check_verbose_name(self, obj, name):
        """Проверка отображаемого имени объекта obj"""
        if '_meta' in obj.__dir__():
            verbose_name = obj._meta.verbose_name
        else:
            verbose_name = obj.verbose_name

        self.assertEqual(
            name, verbose_name, f'Incorrect verbose name: {verbose_name}'
        )

    def check_plural_verbose_name(self, obj, name):
        """Проверка отображаемого имени во множественном числе объекта obj"""
        if '_meta' in obj.__dir__():
            plural_name = obj._meta.verbose_name_plural
        else:
            plural_name = obj.verbose_name_plural

        self.assertEqual(
            name, plural_name, f'Incorrect plural verbose name: {plural_name}'
        )
