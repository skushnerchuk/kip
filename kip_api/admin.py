"""Integrate with admin module."""

from django.contrib import admin

from . import models

MODELS = [
    models.CoursesCategory,
    models.Course,
    models.Lesson,
    models.User,
    models.Profile,
]

for model in MODELS:
    admin.site.register(model)
