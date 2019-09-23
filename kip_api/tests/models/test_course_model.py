from kip_api.models import (
    Courses, CourseGroup, Participation, Lesson, UserLessons
)


def test_course_str_function(prepare_courses):
    field = Courses.objects.first()
    assert field.name == field.__str__()


def test_course_group_str_function(prepare_courses):
    field = CourseGroup.objects.first()
    assert field.name == field.__str__()


def test_str_function(prepare_courses):
    field = Participation.objects.first()
    assert f'{field.user}, {field.group}' == field.__str__()


def test_lesson_str_function(prepare_courses):
    field = Lesson.objects.first()
    assert f'{field.group}: {field.name}' == field.__str__()


def test_user_lessons_str_function(prepare_courses):
    field = UserLessons.objects.first()
    assert f'{field.user} {field.lesson}' == field.__str__()
