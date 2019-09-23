# Вытащено наверх для корректного импорта модели пользователя
from .user import User, Profile  # noqa: F401
from .courses import (
    CourseGroup, Courses, CoursesCategory, Lesson, Participation, UserLessons
)
