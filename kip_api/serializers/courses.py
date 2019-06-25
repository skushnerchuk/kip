from rest_framework import serializers

from kip_api.models import Course, Lesson


class LessonlSerializer(serializers.ModelSerializer):
    """
    Сериализатор урока
    """

    class Meta:
        model = Lesson
        fields = ('pk', 'name', 'description', 'number', 'start', 'duration',)

    name = serializers.CharField()
    description = serializers.CharField()
    number = serializers.IntegerField()
    start = serializers.DateTimeField(required=False)
    duration = serializers.IntegerField()


class CourseCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор курса, включая данные по всем урокам
    """

    class Meta:
        model = Course
        fields = ('category_id', 'name', 'description',)

    category_id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор курса, включая данные по всем урокам
    """

    class Meta:
        model = Course
        fields = ('pk', 'category', 'name', 'description', 'lessons',)

    lessons = LessonlSerializer(source='course_id', many=True)
    category = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()


class CourseListSerializer(serializers.ModelSerializer):
    """
    Сериализатор курса, включая количество уроков в курсе
    """

    class Meta:
        model = Course
        fields = ('pk', 'category', 'name', 'description', 'lessons_count')

    lessons_count = serializers.SerializerMethodField()

    @staticmethod
    def get_lessons_count(pk):
        return Lesson.objects.filter(course=pk).count()

    category = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
