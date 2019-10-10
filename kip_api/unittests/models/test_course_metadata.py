from kip_api.models.courses import (
    CoursesCategory, Courses, CourseGroup, Participation,
    Lesson, UserLessons
)
from kip_api.unittests.base_test import BaseTest


class CoursesCategoryMetadataTest(BaseTest):
    """Тестирование метаданных категорий курсов"""

    def test_model_name(self):
        """Проверка имени модели"""
        model_name = CoursesCategory.objects.first()._meta.model_name
        self.assertEqual(
            'coursescategory',
            model_name,
            f'Incorrect model name: {model_name}')

    def test_model_verbose_name(self):
        """Проверка отображаемого имени поля модели"""
        self.check_verbose_name(CoursesCategory.objects.first())

    def test_model_verbose_plural_name(self):
        """Проверка отображаемого имени поля name во множественном числе"""
        self.check_plural_verbose_name(CoursesCategory.objects.first())

    def test_name_field_unique(self):
        """Проверка уникальности поля name"""
        field = CoursesCategory.objects.first()._meta.get_field('name')
        self.assertTrue(field._unique, 'Field <name> must be unique!')

    def test_fields_exist(self):
        """Проверяем, что присутствуют все поля"""
        fields = ['name']
        self.check_fields_exist(CoursesCategory, fields)

    def test_str_function(self):
        """Проверка работы функции __str__() модели"""
        field = CoursesCategory.objects.first()
        self.assertEqual(
            field.name, field.__str__(),
            'Values of __str__() function result and name field must be equal!'
        )


class CourseMetadataTest(BaseTest):
    """Тестирование метаданных курсов"""

    def test_model_name(self):
        """Проверка имени модели"""
        model_name = Courses.objects.first()._meta.model_name
        self.assertEqual(
            'courses',
            model_name,
            f'Incorrect model name: {model_name}'
        )

    def test_model_verbose_name(self):
        """Проверка отображаемого имени модели"""
        self.check_verbose_name(Courses.objects.first())

    def test_model_verbose_name_plural(self):
        """Проверка отображаемого имени модели во множественном числе"""
        self.check_plural_verbose_name(Courses.objects.first())

    def test_fields_exist(self):
        """Проверяем, что присутствуют все поля"""
        fields = ['name', 'category', 'description', ]
        self.check_fields_exist(Courses, fields)

    def test_str_function(self):
        """Проверка работы функции __str__() модели"""
        field = Courses.objects.first()
        self.assertEqual(
            field.name, field.__str__(),
            'Values of __str__() function result and name field must be equal!'
        )


class CourseGroupMetadataTest(BaseTest):
    """Тестирование метаданных курсов"""

    def test_model_name(self):
        """Проверка имени модели"""
        model_name = CourseGroup.objects.first()._meta.model_name
        self.assertEqual(
            'coursegroup',
            model_name,
            f'Incorrect model name: {model_name}'
        )

    def test_model_verbose_name(self):
        """Проверка отображаемого имени модели"""
        self.check_verbose_name(CourseGroup.objects.first())

    def test_model_verbose_name_plural(self):
        """Проверка отображаемого имени модели во множественном числе"""
        self.check_plural_verbose_name(CourseGroup.objects.first())

    def test_fields_exist(self):
        """Проверяем, что присутствуют все поля"""
        fields = [
            'course', 'name', 'detail_program', 'short_schedule', 'participants', 'closed',
        ]
        self.check_fields_exist(CourseGroup, fields)

    def test_str_function(self):
        """Проверка работы функции __str__() модели"""
        field = CourseGroup.objects.first()
        self.assertEqual(
            field.name, field.__str__(),
            'Values of __str__() function result and name field must be equal!'
        )


class ParticipationMetadataTest(BaseTest):
    """
    Тестирование участия пользователей в группах обучения курсов
    """

    def test_model_name(self):
        """Проверка имени модели"""
        model_name = Participation.objects.first()._meta.model_name
        self.assertEqual(
            'participation',
            model_name,
            f'Incorrect model name: {model_name}'
        )

    def test_model_verbose_name(self):
        """Проверка отображаемого имени модели"""
        self.check_verbose_name(Participation.objects.first())

    def test_model_verbose_name_plural(self):
        """Проверка отображаемого имени модели во множественном числе"""
        self.check_plural_verbose_name(Participation.objects.first())

    def test_fields_exist(self):
        """Проверяем, что присутствуют все поля"""
        fields = [
            'user', 'group', 'role',
        ]
        self.check_fields_exist(Participation, fields)

    def test_str_function(self):
        """Проверка работы функции __str__() модели"""
        field = Participation.objects.first()
        self.assertEqual(
            f'{field.user}, {field.group}', field.__str__(),
            'Values of __str__() function result and name field must be equal!'
        )


class LessonMetadataTest(BaseTest):
    """
    Тестирование участия пользователей в группах обучения курсов
    """

    def test_model_name(self):
        """Проверка имени модели"""
        model_name = Lesson.objects.first()._meta.model_name
        self.assertEqual(
            'lesson',
            model_name,
            f'Incorrect model name: {model_name}'
        )

    def test_model_verbose_name(self):
        """Проверка отображаемого имени модели"""
        self.check_verbose_name(Lesson.objects.first())

    def test_model_verbose_name_plural(self):
        """Проверка отображаемого имени модели во множественном числе"""
        self.check_plural_verbose_name(Lesson.objects.first())

    def test_fields_exist(self):
        """Проверяем, что присутствуют все поля"""
        fields = [
            'group', 'name', 'description', 'number', 'start',
            'duration', 'meeting_url',
        ]
        self.check_fields_exist(Lesson, fields)

    def test_str_function(self):
        """Проверка работы функции __str__() модели"""
        field = Lesson.objects.first()
        self.assertEqual(
            f'{field.group}: {field.name}', field.__str__(),
            'Values of __str__() function result and name field must be equal!'
        )


class UserLessonsMetadataTest(BaseTest):
    """
    Тестирование участия пользователей в группах обучения курсов
    """

    def test_model_name(self):
        """Проверка имени модели"""
        model_name = UserLessons.objects.first()._meta.model_name
        self.assertEqual(
            'userlessons',
            model_name,
            f'Incorrect model name: {model_name}'
        )

    def test_model_verbose_name(self):
        """Проверка отображаемого имени модели"""
        self.check_verbose_name(UserLessons.objects.first())

    def test_model_verbose_name_plural(self):
        """Проверка отображаемого имени модели во множественном числе"""
        self.check_plural_verbose_name(UserLessons.objects.first())

    def test_fields_exist(self):
        """Проверяем, что присутствуют все поля"""
        fields = ['user', 'lesson', 'homework', 'paid']
        self.check_fields_exist(UserLessons, fields)

    def test_str_function(self):
        """Проверка работы функции __str__() модели"""
        field = UserLessons.objects.first()
        self.assertEqual(
            f'{field.user} {field.lesson}', field.__str__(),
            'Values of __str__() function result and name field must be equal!'
        )
