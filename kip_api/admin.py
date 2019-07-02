"""Integrate with admin module."""

from django.contrib import admin

from kip_api.models import courses, user

MODELS = [
    courses.CoursesCategory,
    courses.Courses,
    courses.CourseGroup,
    courses.Participation,
    courses.Lesson,
    courses.UserLessons,

    user.User,
    user.Profile,
]

for model in MODELS:
    admin.site.register(model)
