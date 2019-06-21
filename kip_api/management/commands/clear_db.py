from django.core.management.base import BaseCommand

from kip_api.models import (
    CoursesCategory, Course, User, Profile
)


class Command(BaseCommand):
    help = 'Clear ALL database data'

    def handle(self, *args, **options):
        print('Clear ALL database data')
        User.objects.all().delete()
        CoursesCategory.objects.all().delete()
