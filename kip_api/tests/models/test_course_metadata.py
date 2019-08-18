from django.db import transaction

from kip_api.tests.base_test import BaseTest
from kip_api.models.courses import CoursesCategory
from data_factories import CategoryFactory


class CoursesCategoryMetadataTest(BaseTest):
    """Тестирование метаданных категорий курсов"""

    @classmethod
    def setUpTestData(cls):
        CategoryFactory()

    def test_model_name(self):
        """Проверка имени модели"""
        model_name = CoursesCategory.objects.first()._meta.model_name
        self.assertEqual(
            'coursescategory',
            model_name,
            f'Incorrect model name: {model_name}')

    def test_model_verbose_name(self):
        """Проверка отображаемого имени поля name"""
        self.check_verbose_name(CoursesCategory.objects.first(), 'Категория')

    def test_model_verbose_plural_name(self):
        """Проверка отображаемого имени поля name во множественном числе"""
        self.check_plural_verbose_name(CoursesCategory.objects.first(), 'Категории курсов')

    def test_name_field_exist(self):
        """Проверка существования поля name"""
        self.assertTrue(
            self.field_exist(CoursesCategory, 'name'),
            'Field <name> must exist!'
        )

    def test_name_field_unique(self):
        """Проверка уникальности поля name"""
        field = CoursesCategory.objects.first()._meta.get_field('name')
        self.assertTrue(field._unique, 'Field <name> must be unique!')

    def test_str_function(self):
        """Проверка работы функции __str__() модели"""
        field = CoursesCategory.objects.first()
        self.assertEqual(
            field.name, field.__str__(),
            'Values of __str__() function result and name field must be equal!'
        )
