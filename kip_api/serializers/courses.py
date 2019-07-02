from rest_framework import serializers

from kip_api.models.courses import Course, Lesson


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
    Сериализатор создания курса
    """

    class Meta:
        model = Course
        fields = ('category_id', 'name', 'description',)

    category_id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()


class CourseDeleteSerializer(serializers.ModelSerializer):
    """
    Сериализатор удаления курса
    """

    class Meta:
        model = Course
        fields = ('pk',)

    pk = serializers.IntegerField()


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

    def create(self, validated_data):
        return Course(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('', instance.name)
        instance.description = validated_data.get('', instance.description)
        instance.detail_program = validated_data.get('', instance.detail_program)
        instance.save()
        return instance


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
