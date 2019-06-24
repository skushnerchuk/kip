import factory
from django.db.models.signals import post_save
from django.core.management.base import BaseCommand, no_translations

from kip_api.models import (
    CoursesCategory, Course, User, Profile, Lesson
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
        model = Course

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


@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):
    """
    Фабрика пользователей. Отключаем также сигнал post_save, так как профили мы будем создавать сами,
    и письма отправлять никому не хотим
    """
    class Meta:
        model = User

    email = factory.Sequence(lambda n: 'user{}@example.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', '1234567890')
    profile = factory.RelatedFactory(ProfileFactory, 'user')


class LessonFactory(factory.django.DjangoModelFactory):
    """
    Фабрика уроков
    Имя урока генерируется по шаблону Lesson_N
    """
    class Meta:
        model = Lesson

    # Должен быть передан параметр course, который указывает к какому курсу относится урок
    course = factory.SelfAttribute('course')

    number = factory.Sequence(lambda n: '{}'.format(n))
    description = factory.Faker('text')
    name = factory.Sequence(lambda n: 'Lesson {}'.format(n))


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
            '--lessons', action='store', help='Count of lessons in each course', type=int, default=1
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
    def generate_lessons(count):
        courses = Course.objects.all()
        for c in courses:
            # Отсчет номеров уроков ведем с 1
            LessonFactory.reset_sequence(1)
            for i in range(count):
                LessonFactory(course=c)
            # Начинаем нумировать уроки заново
            LessonFactory.reset_sequence(1)

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
            lessons_count = options['lessons']

            print('Generating {} users...'.format(users_count))
            self.generate_users(users_count)
            print('Generating {} categories...'.format(categories_count))
            self.generate_categories(categories_count)
            print('Generating {} courses per category...'.format(courses_count))
            self.generate_courses(courses_count)
            print('Generating {} lessons per course...'.format(lessons_count))
            self.generate_lessons(lessons_count)
