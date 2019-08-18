from datetime import datetime, date

import factory
from django.db import transaction

from kip_api.models.user import User, Profile
from kip_api.models.courses import (
    CoursesCategory, Courses, CourseGroup, Lesson, UserLessons
)


class CategoryFactory(factory.django.DjangoModelFactory):
    """
    Фабрика категорий курсов
    Имена категорий генерируются по шаблону: Category_N
    """

    class Meta:
        model = CoursesCategory

    name = factory.Sequence(lambda n: 'Category {}'.format(n))


class CourseFactory(factory.django.DjangoModelFactory):
    """
    Фабрика курсов
    Имена курсов генерируются по шаблону: Course_N
    Описание заполняется случайным текстом
    """

    class Meta:
        model = Courses

    # Должен быть передан параметр category, который указывает к какой категории относится курс
    category = factory.SelfAttribute('category')
    name = factory.Sequence(lambda n: 'Course {}'.format(n))
    description = factory.Faker('text')


class ProfileFactory(factory.django.DjangoModelFactory):
    """
    Фабрика профилей пользователей
    """

    class Meta:
        model = Profile

    user = factory.SubFactory('kip_api.factories.UserFactory', profile=None)
    biography = factory.Faker('text')
    birth_date = date.today()


class UserFactory(factory.django.DjangoModelFactory):
    """
    Фабрика пользователей. Если есть необходимость изменить домен почты,
    то следует внести соответствующие изменения в EmailMixin, чтобы избежать
    отправки почты для тестовых аккаунтов
    """

    class Meta:
        model = User

    email = factory.Sequence(lambda n: 'user{}@example.com'.format(n))
    email_confirmed = True
    password = factory.PostGenerationMethodCall('set_password', '1234567890')
    profile = factory.RelatedFactory(ProfileFactory, 'user')


class UserFactoryCustom(factory.django.DjangoModelFactory):
    """
    Фабрика пользователей. Если есть необходимость изменить домен почты,
    то следует внести соответствующие изменения в EmailMixin, чтобы избежать
    отправки почты для тестовых аккаунтов
    """

    class Meta:
        model = User

    email = factory.SelfAttribute('email')
    email_confirmed = bool(factory.SelfAttribute('email_confirmed'))
    password = factory.PostGenerationMethodCall('set_password', factory.SelfAttribute('password'))
    profile = factory.RelatedFactory(ProfileFactory, 'user')


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseGroup

    # Должен быть передан параметр group, который указывает
    # к какому курсу относится группа
    course = factory.SelfAttribute('course')
    name = factory.Sequence(lambda n: 'Group {}'.format(n))


class LessonFactory(factory.django.DjangoModelFactory):
    """
    Фабрика уроков
    Имя урока генерируется по шаблону Lesson_N
    """

    class Meta:
        model = Lesson

    # Должен быть передан параметр group, который указывает к какому курсу относится урок
    group = factory.SelfAttribute('group')
    number = factory.Sequence(lambda n: '{}'.format(n))
    description = factory.Faker('text')
    name = factory.Sequence(lambda n: 'Lesson {}'.format(n))
    start = datetime.now()

    @staticmethod
    def generate_users(count):
        User.objects.all().delete()
        for c in range(count):
            UserFactory()

    @staticmethod
    def generate_categories(count):
        CoursesCategory.objects.all().delete()
        for c in range(count):
            CategoryFactory()

    @staticmethod
    def generate_courses(count):
        categories = CoursesCategory.objects.all()
        for c in categories:
            for i in range(count):
                CourseFactory(category=c)

    @staticmethod
    def generate_groups(count):
        courses = Courses.objects.all()
        for c in courses:
            print(c)
            for i in range(count):
                GroupFactory(course=c)

    @staticmethod
    def generate_lessons(count):
        groups = CourseGroup.objects.all()
        for c in groups:
            # Отсчет номеров уроков ведем с 1
            LessonFactory.reset_sequence(1)
            for i in range(count):
                LessonFactory(group=c)
            # Начинаем нумировать уроки заново
            LessonFactory.reset_sequence(1)
        # Теперь записываем пользователей в группы. Каждого пользователя
        # записываем на каждый курс, в целях получения нагрузки
        users = User.objects.all()
        groups = CourseGroup.objects.all()
        with transaction.atomic():
            for user in users:
                for group in groups:
                    lessons = group.lesson_set.all()
                    user.groups.add(group)
                    user.save()
                    # Формируем для него расписание
                    for l in lessons:
                        print('{} {}'.format(user.email, l.name))
                        UserLessons.objects.create(
                            lesson_id=l.pk,
                            user_id=user.pk
                        ).save()

    @staticmethod
    def clear():
        print('Clear ALL database data')
        User.objects.all().delete()
        CoursesCategory.objects.all().delete()


def generate_users(count):
    for c in range(count):
        UserFactory()


def generate_categories(count):
    for c in range(count):
        CategoryFactory()


def generate_courses(count):
    categories = CoursesCategory.objects.all()
    for c in categories:
        for i in range(count):
            CourseFactory(category=c)


def generate_groups(count):
    courses = Courses.objects.all()
    for c in courses:
        print(c)
        for i in range(count):
            GroupFactory(course=c)


def generate_lessons(count):
    groups = CourseGroup.objects.all()
    for c in groups:
        # Отсчет номеров уроков ведем с 1
        LessonFactory.reset_sequence(1)
        for i in range(count):
            LessonFactory(group=c)
        # Начинаем нумировать уроки заново
        LessonFactory.reset_sequence(1)
    # Теперь записываем пользователей в группы. Каждого пользователя
    # записываем на каждый курс, в целях получения нагрузки
    users = User.objects.all()
    groups = CourseGroup.objects.all()
    with transaction.atomic():
        for user in users:
            for group in groups:
                lessons = group.lesson_set.all()
                user.groups.add(group)
                user.save()
                # Формируем для него расписание
                for l in lessons:
                    print('{} {}'.format(user.email, l.name))
                    UserLessons.objects.create(
                        lesson_id=l.pk,
                        user_id=user.pk
                    ).save()


def clear():
    print('Clear ALL database data')
    User.objects.all().delete()
    CoursesCategory.objects.all().delete()
