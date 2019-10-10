# Вытащено наверх для корректного импорта модели пользователя
from kip_api.models.user import User, Profile  # flake8: noqa F401
from .courses import (
    CourseGroup, Courses, CoursesCategory, Lesson, Participation, UserLessons  # flake8: noqa F401
)
