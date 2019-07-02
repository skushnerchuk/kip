"""Integrate with admin module."""

from django.contrib import admin

from kip_api.models import courses

MODELS = [
    courses.CoursesCategory,
    courses.Course,
    courses.Lesson,
    courses.User,
    courses.Profile,
]

for model in MODELS:
    admin.site.register(model)
