from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _


#
# Пользователи курсов, а так же преподаватели
#

class UserManager(BaseUserManager):
    """
    Менеджер управления пользователями
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Собственная модель пользователя
    """

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    # Логин гасим - он нам не понадобиться, вход будет по почте
    username = None
    # Делаем почту уникальным полем
    email = models.EmailField(_('адрес'), unique=True)
    email_confirmed = models.BooleanField(_('почта подтверждена'), blank=False, default=False)
    # Группы курсов, на которые записан пользователь
    # Теперь логин - это почта
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Пользователь не может участвовать одновременно более чем в одной группе курса
    groups = models.ManyToManyField('CourseGroup', blank=True)

    objects = UserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    """
    Профиль пользователя
    """

    class Meta:
        db_table = 'profiles'
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        app_label = 'kip_api'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Дата рождения
    birth_date = models.DateField(_('Дата рождения'), null=True, blank=True)
    # Информация о себе (заполняет пользователь)
    biography = models.TextField(_('О себе'), blank=True)

    def __str__(self):
        return 'Профиль {}'.format(self.user.email)


#
# Собственно курсы и расписание
#

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
    его могут проходить несколько групп одновременно, возможно, со сдвижкой начала
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
    # Ссылка на документс детальной прогаммой курса, БЕЗ привязки
    # к расписанию.
    # Учитывая высказывание выше о возможности изменения программы от курса группы к группе,
    # конкретную программу курса также необходимо сохранять и в группе курса dj
    # избежание недоразумений.
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
        verbose_name_plural = 'Группы курсов'
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
    # lessons расписание занятий этой группы


class GroupSchedule(models.Model):
    """
    Расписание группы
    """
    pass


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
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, verbose_name=_('Курс'), related_name='course_id')
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
    Модуль курса
    """

    class Meta:
        db_table = 'modules'
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'

    # Курс к которому относится модуль
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE,
        verbose_name=_('Курс'), related_name='course_id'
    )
    # Наименование модуля
    name = models.CharField(max_length=255, verbose_name=_('Название'))
