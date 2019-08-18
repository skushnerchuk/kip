from django.test import TestCase
from django.db import models

from data_factories import (
    generate_courses, generate_categories, generate_groups,
    generate_lessons, generate_users
)


class BaseTest(TestCase):
    """
    Базовый класс тестов
    """

    @classmethod
    def setUpTestData(cls):
        generate_users(1)
        generate_categories(1)
        generate_courses(1)
        generate_groups(1)
        generate_lessons(1)

    @staticmethod
    def field_exist(model_object, field):
        """Проверяем наличие поля field в модели model"""
        try:
            model_object._meta.get_field(field)
            return True
        except models.FieldDoesNotExist:
            return False

    def check_verbose_name(self, obj):
        """Проверка отображаемого имени объекта obj."""
        if '_meta' in obj.__dir__():
            verbose_name = obj._meta.verbose_name
        else:
            verbose_name = obj.verbose_name

        self.assertNotEqual(
            '', verbose_name, f'Verbose name must have a value'
        )
        self.assertIsNotNone(
            verbose_name, f'Verbose name must have a value'
        )

    def check_plural_verbose_name(self, obj):
        """
        Проверка отображаемого имени во множественном числе объекта obj
        """
        if '_meta' in obj.__dir__():
            plural_name = obj._meta.verbose_name_plural
        else:
            plural_name = obj.verbose_name_plural

        self.assertNotEqual(
            '', plural_name, f'Plural verbose name must have a value'
        )
        self.assertIsNotNone(
            plural_name, f'Plural verbose name must have a value'
        )

    def check_fields_exist(self, model, fields):
        """Проверяем, что присутствуют все поля"""
        obj = model.objects.first()
        absent = [f for f in fields if not self.field_exist(obj, f)]
        self.assertListEqual(
            absent, [],
            f'The field(s) <{",".join(absent)}> must be exist!'
        )
