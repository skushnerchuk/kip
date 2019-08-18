from django.core.management.base import BaseCommand, no_translations
from django.db import transaction

from kip_api.models.user import User
from kip_api.models.courses import (
    CoursesCategory, Courses, CourseGroup, UserLessons,
)

import data_factories as df


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

    @no_translations
    def handle(self, *args, **options):
        if options['clear']:
            df.clear()
            return

        if options['fill']:
            # Всегда очищаем базу перед заполнением новыми данными
            df.clear()
            users_count = options['users']
            categories_count = options['categories']
            courses_count = options['courses']
            groups_count = options['groups']
            lessons_count = options['lessons']

            print('Generating {} users...'.format(users_count))
            df.generate_users(users_count)
            print('Generating {} categories...'.format(categories_count))
            df.generate_categories(categories_count)
            print('Generating {} courses per category...'.format(courses_count))
            df.generate_courses(courses_count)
            print('Generating {} groups per course...'.format(groups_count))
            df.generate_groups(groups_count)
            print('Generating {} lessons per course...'.format(lessons_count))
            df.generate_lessons(lessons_count)
