from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.mail import EmailMessage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from kip.settings import EMAIL_INFORMATOR
from .utils import token_generator, create_email_confirm_url


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


class CoursesCategory(models.Model):
    """
    Категории курсов
    """

    class Meta:
        db_table = 'courses_categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории курсов'

    name = models.CharField(max_length=100, unique=True, default='Новая категория')

    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Курс обучения
    """

    class Meta:
        db_table = 'courses'
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    category = models.ForeignKey(CoursesCategory, on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.name


class Lesson(models.Model):
    """
    Занятие в рамках курса
    """

    class Meta:
        db_table = 'lessons'
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        unique_together = ('course', 'name')

    # Курс к которому относится занятие
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_('Курс'), related_name='course_id')
    # Краткое наименование урока
    name = models.CharField(max_length=255, verbose_name=_('Название'))
    # Полное описание урока
    description = models.TextField(verbose_name=_('Описание'))
    # Порядковый № урока в курсе
    number = models.IntegerField(verbose_name=_('№ урока в курсе'))
    # Дата и время начала занятия
    start = models.DateTimeField(verbose_name=_('Начало'), blank=True, null=True)
    # Длительность в условных часах (например академических или астрономических)
    duration = models.IntegerField(verbose_name=_('Длительность'), default=2)

    def __str__(self):
        return self.name


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
    # Курсы, на которые записан пользователь
    courses = models.ManyToManyField(Course, blank=True)

    # Теперь логин - это пароль
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Дата рождения
    birth_date = models.DateField(_('Дата рождения'), null=True, blank=True)
    # Информация о себе (заполняет пользователь)
    biography = models.TextField(_('О себе'), blank=True)

    def __str__(self):
        return 'Профиль {}'.format(self.user.email)


##################
#
# Events listeners
#
# Служат для создания/обновления профиля пользователя без обращения к методу save() объекта user.profile
#
@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return
    print('Create profile')
    Profile.objects.create(user=instance)
    # Отправляем пользователю ссылку на подтверждение почты
    # Это место потенциальной проблемы, если почтовый сервер недоступен
    # TODO Сделать отправку писем асихронно, через RabbitMQ, Celery или еще как. Переделать письмо на нормальные шаблоны
    token = token_generator.make_token(instance)
    url = create_email_confirm_url(instance.pk, token)
    email = EmailMessage()
    email.content_subtype = 'html'
    email.subject = 'Подтвердите регистрацию аккаунта'
    email.body = '<a href="{}" target="_blank">Перейдите по ссылке для подтверждения</a>'.format(url)
    email.from_email = EMAIL_INFORMATOR
    email.to = [instance.email]
    email.send(fail_silently=True)


@receiver(post_save, sender=get_user_model())
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
