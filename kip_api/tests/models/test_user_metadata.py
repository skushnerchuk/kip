import logging

from django.core.management.base import no_translations

from kip_api.tests.base_test import BaseTest
from kip_api.models.user import User, Profile
from data_factories import UserFactoryCustom


class UserModelMetadataTest(BaseTest):
    """
    Тестирование метаданных пользовательской модели
    Мы не хотим, чтобы изменения метаданных проходили мимо тестов,
    поэтому будем их проверять. Для упрощения не будут проверятся типы полей,
    их размерности и т.п.
    Также здесь будет проверяться модель Profile, как неразрывно связанная
    с моделью User
    """

    # Метаданные самой модели

    @classmethod
    def setUpTestData(cls):
        # Гасим логи от factory_boy, они нам не нужны
        logging.getLogger('faker').setLevel(logging.ERROR)
        # Домен должен быть example.com, иначе будет выполнена
        # отправка почты по указанному адресу
        UserFactoryCustom(
            email='test@example.com',
            email_confirmed=True,
            password='1234567890'
        )

    def test_model_name(self):
        """Проверка имени модели"""
        model_name = User.objects.first()._meta.model_name
        self.assertEqual(
            'user',
            model_name,
            f'Incorrect user model name: {model_name}')

    def test_model_verbose_name(self):
        """Проверка отображаемого названия модели"""
        self.check_verbose_name(User.objects.first(), 'Пользователь')

    def test_model_verbose_name_plural(self):
        """Проверка отображаемого названия модели во множественном числе"""
        self.check_plural_verbose_name(User.objects.first(), 'Пользователи')

    # Метаданные поля email

    def test_email_field_exist(self):
        """Проверяем наличие поля email"""
        self.assertTrue(
            self.field_exist(User, 'email'),
            'The field <email> must be exist!'
        )

    def test_email_field_unique(self):
        """Проверяем уникальность поля email"""
        field = User.objects.first()._meta.get_field('email')
        self.assertTrue(field._unique, 'Email field must be unique!')

    def test_email_verbose_name(self):
        """Проверка отображаемого названия поля email"""
        field = User.objects.first()._meta.get_field('email')
        self.check_verbose_name(field, 'адрес')

    # Метаданные поля email_confirmed

    def test_email_confirmed_field_exist(self):
        """Проверяем наличие поля email_confirmed"""
        self.assertTrue(
            self.field_exist(User, 'email_confirmed'),
            'The field <email_confirmed> must be exist!'
        )

    def test_email_confirmed_verbose_name(self):
        """Проверка отображаемого названия поля email_confirmed"""
        self.check_verbose_name(User.objects.first()._meta.get_field('email_confirmed'), 'почта подтверждена')

    def test_user_disabled_fields(self):
        """Проверяем, что отсутствуют поля, которые мы перекрываем"""
        fields = ['username', 'first_name', 'last_name', ]
        absent = [f for f in fields if self.field_exist(User, f)]
        self.assertListEqual(
            absent, [],
            f'The field(s) <{",".join(absent)}> must be absent!'
        )

    def test_username_field(self):
        """Проверяем, что USERNAME_FIELD выставлен в модели правильно"""
        self.assertEqual(
            User.USERNAME_FIELD, 'email',
            'Field USERNAME_FIELD must be equal "email"'
        )

    def test_required_fields(self):
        """проверяем, что поле REQUIRED_FIELDS пустое"""
        self.assertListEqual(
            User.REQUIRED_FIELDS, [],
            'Field REQUIRED_FIELD must be empty'
        )

    def test_groups_field_exist(self):
        """Проверяем наличие поля groups"""
        self.assertTrue(
            self.field_exist(User, 'groups'),
            'The field <groups> must be exist!'
        )

    def test_user_str_method(self):
        """Проверка метода __str__ - он должен возвращать почту пользователя"""
        user = User.objects.first()
        self.assertEqual(
            user.__str__(), user.email,
            'Values of __str__() function and email field must be equal!'
        )

    def test_profile_model_name(self):
        """Проверяем корректность имени модели"""
        model_name = Profile.objects.get(user_id=1)._meta.model_name
        self.assertEqual(
            model_name, 'profile',
            f'Profile model incorrect name: {model_name}'
        )

    def test_profile_fields(self):
        """Проверяем, что присутствуют все поля"""
        fields = [
            'user', 'birth_date', 'biography', 'first_name',
            'middle_name', 'last_name',
        ]
        absent = [f for f in fields if not self.field_exist(Profile, f)]
        self.assertListEqual(
            absent, [],
            f'The field(s) <{",".join(absent)}> must be exist!'
        )

    def test_profile_str_method(self):
        """Проверка метода __str__()"""
        profile = Profile.objects.get(user_id=1)
        self.assertEqual(profile.__str__(), f'Профиль: {profile.user.email}')

    def test_profile_birth_date_verbose_name(self):
        self.check_verbose_name(
            Profile.objects.get(user_id=1)._meta.get_field('birth_date'),
            'Дата рождения'
        )

    def test_profile_biography_verbose_name(self):
        self.check_verbose_name(
            Profile.objects.get(user_id=1)._meta.get_field('biography'),
            'О себе'
        )

    def test_profile_first_name_verbose_name(self):
        self.check_verbose_name(
            Profile.objects.get(user_id=1)._meta.get_field('first_name'),
            'Имя'
        )

    def test_profile_middle_name_verbose_name(self):
        self.check_verbose_name(
            Profile.objects.get(user_id=1)._meta.get_field('middle_name'),
            'Отчество'
        )

    def test_profile_last_name_verbose_name(self):
        self.check_verbose_name(
            Profile.objects.get(user_id=1)._meta.get_field('last_name'),
            'Фамилия'
        )
