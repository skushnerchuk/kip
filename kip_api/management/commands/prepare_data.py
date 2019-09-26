from datetime import datetime, date

import factory
from django.core.management.base import BaseCommand, no_translations
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


class Command(BaseCommand):
    help = 'Manage database data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true', help='Clear ALL data in database',
        )

        parser.add_argument(
            '--fill', action='store_true', help='Generate random data',
        )

        parser.add_argument(
            '--users', action='store', help='Count of users', type=int, default=1
        )
        parser.add_argument(
            '--categories', action='store', help='Count of categories', type=int, default=1
        )
        parser.add_argument(
            '--courses', action='store', help='Count of courses in each category', type=int, default=1
        )
        parser.add_argument(
            '--groups', action='store', help='Count of groups in each course', type=int, default=1
        )
        parser.add_argument(
            '--lessons', action='store', help='Count of lessons in each group', type=int, default=1
        )

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
    def generate_lessons(count): # flake8: noqa C901
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

    @no_translations
    def handle(self, *args, **options):
        if options['clear']:
            self.clear()
            return

        if options['fill']:
            # Всегда очищаем базу перед заполнением новыми данными
            self.clear()
            users_count = options['users']
            categories_count = options['categories']
            courses_count = options['courses']
            groups_count = options['groups']
            lessons_count = options['lessons']

            print('Generating {} users...'.format(users_count))
            self.generate_users(users_count)
            print('Generating {} categories...'.format(categories_count))
            self.generate_categories(categories_count)
            print('Generating {} courses per category...'.format(courses_count))
            self.generate_courses(courses_count)
            print('Generating {} groups per course...'.format(groups_count))
            self.generate_groups(groups_count)
            print('Generating {} lessons per course...'.format(lessons_count))
            self.generate_lessons(lessons_count)
