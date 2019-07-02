from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CoursesCategory(models.Model):
    """
    Категории курсов
    """

    class Meta:
        db_table = 'courses_categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории курсов'
        app_label = 'kip_api'

    name = models.CharField(max_length=100, unique=True, default='Новая категория')

    def __str__(self):
        return self.name


class Courses(models.Model):
    """
    Курсы
    """

    class Meta:
        db_table = 'courses'
        verbose_name = 'Наименование курса'
        verbose_name_plural = 'Наименования курсов'
        app_label = 'kip_api'
        unique_together = ('category', 'name')

    # Наименование курса (уникальное в рамках категории)
    name = models.CharField(max_length=100, default='Новый курс')
    # Категория, к которой относится курс
    category = models.ForeignKey(
        CoursesCategory,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    # Описание курса
    description = models.TextField(verbose_name='Описание', blank=True)

    def __str__(self):
        return self.name


class CourseGroup(models.Model):
    """
    Группа курса
    -------------
    Одному и тому же курсу могут соответствовать несколько расписаний, то есть
    его могут проходить несколько групп одновременно, возможно, со сдвигом начала
    обучения во времени. Логично предположить, что и программы групп могут несколько
    отличаться, напрмер, если программа была уточнена, а предыдущие группы
    обучение по ранее согласованной программе еще не закончили.
    """

    class Meta:
        db_table = 'courses_groups'
        verbose_name = 'Группа курса'
        verbose_name_plural = 'Группы курсов'
        app_label = 'kip_api'
        unique_together = ('course', 'name')

    course = models.ForeignKey(
        Courses,
        on_delete=models.CASCADE,
        verbose_name='Курс'
    )
    # Наименование группы (уникальное в рамках курса)
    name = models.CharField(max_length=255, verbose_name='Название')
    # Ссылка на документ с детальной программой курса
    detail_program = models.URLField(verbose_name='Ссылка на программу курса', blank=True)
    # Краткое недельное расписание занятий
    # Например: 6 академических часов в неделю, 2 занятия, вт. и чт, с 20:00
    short_schedule = models.CharField(max_length=255, blank=True, verbose_name='Недельное расписание')
    # Кто участвует в этой группе
    participants = models.ManyToManyField(
        get_user_model(),
        through='Participation',
        related_name='courses_groups',
    )
    # Обучение в этой группе закончено
    closed = models.BooleanField(verbose_name='Обучение закончено', default=False)

    def __str__(self):
        return self.name


class Participation(models.Model):
    """
    Участие пользователей в группах обучения
    """

    ROLE_STUDENT = 1
    ROLE_TEACHER = 2

    ROLE_CHOICES = (
        (ROLE_STUDENT, _('Студент')),
        (ROLE_TEACHER, _('Преподаватель'))
    )

    class Meta:
        db_table = 'participations'
        verbose_name = 'Участие в группах'
        verbose_name_plural = 'Участие в группах'
        app_label = 'kip_api'
        unique_together = ('user', 'group')

    # Пользователь
    user = models.ForeignKey(get_user_model(), related_name='participations', on_delete=models.CASCADE)
    # Учебная группа курса
    group = models.ForeignKey(CourseGroup, related_name='participations', on_delete=models.CASCADE)
    # Роль пользователя в группе
    role = models.IntegerField(choices=ROLE_CHOICES, default=ROLE_STUDENT)

    def __str__(self):
        return '{}, {}'.format(self.user, self.group)


class Lesson(models.Model):
    """
    Занятие в рамках группы курса
    Так как занятия от курса к курсу могут меняться, то логично
    их привязывать не к курсу, а к группе курса
    """

    class Meta:
        db_table = 'lessons'
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        unique_together = ('group', 'name')
        app_label = 'kip_api'

    # Группа, к которой относится урок
    group = models.ForeignKey(CourseGroup, on_delete=models.CASCADE, verbose_name=_('Учебная группа'))
    # Краткое наименование урока (уникальное в рамках текущей группы)
    name = models.CharField(max_length=255, verbose_name=_('Название'))
    # Полное описание урока
    description = models.TextField(verbose_name=_('Описание'))
    # Порядковый № урока в курсе
    number = models.IntegerField(verbose_name=_('№ урока в курсе'))
    # Дата и время начала занятия
    start = models.DateTimeField(verbose_name=_('Начало'), blank=True)
    # Длительность в условных часах (например академических или астрономических)
    duration = models.IntegerField(verbose_name=_('Длительность'), default=2)
    # Ссылка на площадку вебинара
    meeting_url = models.URLField(verbose_name=_('Ссылка на вебинар'), null=True, blank=True)

    def __str__(self):
        return '{}: {}'.format(self.group, self.name)


class UserLessons(models.Model):
    """
    Связь уроков группы с учениками
    По этой таблице определяется, разрешен ли доступ ученика к уроку, сдано или нет домашнее задание
    """

    # Статусы домашних заданий
    # Задание не сдано
    HOMEWORK_NOT_SUBMITTED = 0
    # Задание отправлено на доработку после проверки
    HOMEWORK_REJECTED = 1
    # Задание принято
    HOMEWORK_ACCEPTED = 2
    # Задание отправлено на проверку
    HOMEWORK_SENT_FOR_REVIEW = 3
    # Задание принято на проверку
    HOMEWORK_ON_REVIEW = 4
    # Задание не задано
    HOMEWORK_NOT_EXIST = 5

    HOMEWORK_CHOICES = (
        (HOMEWORK_NOT_EXIST, _('Не задано')),
        (HOMEWORK_NOT_SUBMITTED, _('Не сдано')),
        (HOMEWORK_REJECTED, _('Отправлено на доработку')),
        (HOMEWORK_ACCEPTED, _('Принято')),
        (HOMEWORK_SENT_FOR_REVIEW, _('Отправлено на проверку')),
        (HOMEWORK_ON_REVIEW, _('Принято на проверку')),
    )

    class Meta:
        db_table = 'lessons_status'
        verbose_name = ''
        verbose_name_plural = 'Занятия пользователей'
        app_label = 'kip_api'
        unique_together = ('user', 'lesson')

    # Пользователь
    user = models.ForeignKey(
        get_user_model(),
        related_name='lessons_status',
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь')
    )
    # Урок в рамках группы курса
    lesson = models.ForeignKey(
        Lesson,
        related_name='lessons_status',
        on_delete=models.CASCADE,
        verbose_name=_('Урок')
    )
    # Статус домашнего задания
    homework = models.IntegerField(
        choices=HOMEWORK_CHOICES,
        default=HOMEWORK_NOT_SUBMITTED,
        verbose_name=_('Домашнее задание')
    )
    # Урок оплачен или нет. Ссылка на вебинар и сдача домашнего задания будет доступна
    # пользователю только если урок оплачен
    paid = models.BooleanField(default=False, verbose_name=_('оплачено'))

    def __str__(self):
        return '{} {}'.format(self.user, self.lesson)
