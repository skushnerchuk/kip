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


class Course(models.Model):
    """
    Курс обучения
    -------------
    В рамках одной категории курсы должны иметь разные имена.
    Одному и тому же курсу могут соответствовать несколько расписаний, то есть
    его могут проходить несколько групп одновременно, возможно, со сдвигом начала
    обучения во времени. Логично предположить, что и программы групп могут несколько
    отличаться, напрмер, если программа была уточнена, а предыдущие группы
    обучение по ранее согласованной программе еще не закончили.
    """

    class Meta:
        db_table = 'courses'
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        app_label = 'kip_api'
        unique_together = ('category', 'name')

    category = models.ForeignKey(
        CoursesCategory,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    # Наименование курса
    name = models.CharField(max_length=255, verbose_name='Название')
    # Описание курса
    description = models.TextField(verbose_name='Описание', blank=True)
    # Ссылка на документ с детальной прогаммой курса, БЕЗ привязки
    # к расписанию.
    # Учитывая высказывание выше о возможности изменения программы курса от группы к группе,
    # конкретную программу курса также необходимо сохранять и в группе курса во избежание недоразумений.
    detail_program = models.URLField(vebose_name='Ссылка на программу курса', blank=True)

    def __str__(self):
        return self.name


class CourseGroup(models.Model):
    """
    Группа курса
    """

    class Meta:
        db_table = 'courses_groups'
        verbose_name = 'Группа курса'
        verbose_name_plural = 'Группы курса'
        unique_together = ('course', 'name')
        app_label = 'kip_api'

    # Курс к которому относится группа
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_('Курс'),
        related_name='course_id'
    )
    # Наименование группы
    name = models.CharField(
        max_length=255,
        verbose_name=_('Название группы')
    )
    # Ссылка на программу курса для этой группы
    detail_program = models.URLField(
        vebose_name='Ссылка на программу курса', blank=True
    )
    # Открыта ли эта группа для набора. В рамках курса в один момент может быть открыто
    # несколько групп, которые, например, имеют разное расписание
    is_opened = models.BooleanField(default=False, verbose_name='Открыта для набора')
    # Предполагаемое недельное расписание занятий группы. Носит чисто информативный характер,
    # на основании чего пользователь может выбрать группу с подходящим для него расписанием
    weekly_schedule = models.CharField(max_length=255, blank=True, verbose_name='Недельное расписание')


class Lesson(models.Model):
    """
    Занятие в рамках текущей группы курса
    Так как занятия от курса к курсу могут меняться, то логично
    их привязывать не к курсу, а к группе курса
    """

    class Meta:
        db_table = 'lessons'
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        unique_together = ('course', 'name')
        app_label = 'kip_api'

    # Модуль к которому относится занятие
    module = models.ForeignKey('CourseModule', on_delete=models.CASCADE, verbose_name=_('Курс'),
                               related_name='course_id')
    # Краткое наименование урока
    name = models.CharField(max_length=255, verbose_name=_('Название'))
    # Полное описание урока
    description = models.TextField(verbose_name=_('Описание'))
    # Порядковый № урока в курсе
    number = models.IntegerField(verbose_name=_('№ урока в курсе'))
    # Дата и время начала занятия
    start = models.DateTimeField(verbose_name=_('Начало'), blank=True)
    # Длительность в условных часах (например академических или астрономических)
    duration = models.IntegerField(verbose_name=_('Длительность'), default=2)

    def __str__(self):
        return self.name


class CourseModule:
    """
    Модуль курса для конкретной группы
    Вынесен в отдельную сущность, так как расписание может уточняться от
    группы к группе
    ----------------------------------
    Модуль - минимальная единица, которая может быть оплачена обучающимся
    При оплате всего курса для оплатившего все модули помечаются как оплаченные
    В теории модуль может иметь только 1 занятия, но логичнее ставить в модуль
    столько занятий, чтобы с учетом недельного расписания в нем находился условный
    месяц (например, 4 недели), за исключением определенных ситуаций, например,
    подготовки выпускного проекта, когда имеет смысл 1 или 2 занятия за этот период.
    Стоимость модуля рассчитывается исходя из стоимости всего курса.
    """

    class Meta:
        db_table = 'modules'
        verbose_name = 'Модуль занятий'
        verbose_name_plural = 'Модули занятий'

    # Курс к которому относится модуль
    course = models.ForeignKey(
        CourseGroup, on_delete=models.CASCADE,
        verbose_name=_('Группа курса'), related_name='group_id'
    )
    # Наименование модуля
    name = models.CharField(max_length=255, verbose_name=_('Название модуля'))
