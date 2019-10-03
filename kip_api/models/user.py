from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _

from kip_api.utils import image_file_name


#
# Участники курсов (студенты и преподаватели)
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
        if 'is_superuser' in extra_fields:
            user.email_confirmed = True
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user = self._create_user(email, password, **extra_fields)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        # Для суперпользователя профиль создаем принудительно
        user = self._create_user(email, password, **extra_fields)
        profile = Profile.objects.create(user=user)
        profile.role = Profile.ROLE_SUPERUSER
        profile.save(using=self.db)
        return user


class User(AbstractUser):
    """
    Собственная модель пользователя
    """

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        app_label = 'kip_api'

    # Логин гасим - он нам не понадобиться, вход будет по почте
    username = None
    # Гасим first_name, last_name - у нас это будет в профиле
    first_name = None
    last_name = None
    # Делаем почту уникальным полем
    email = models.EmailField(_('адрес'), unique=True)
    email_confirmed = models.BooleanField(_('почта подтверждена'), blank=False, default=False)
    # Теперь логин - это почта
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
    # Учебные группы, где участвует пользователь
    groups = models.ManyToManyField(
        to='CourseGroup',
        through='Participation',
        related_name='users',
        blank=True, verbose_name=_('Учебные группы')
    )

    def __str__(self):
        return self.email


class Profile(models.Model):
    """
    Профиль пользователя
    """

    ROLE_SUPERUSER = 0
    ROLE_USER = 1
    ROLE_TEACHER = 2

    ROLE_CHOICES = (
        (ROLE_SUPERUSER, _('Администратор')),
        (ROLE_USER, _('Студент')),
        (ROLE_TEACHER, _('Преподаватель'))
    )

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
    # Имя
    first_name = models.CharField(_('Имя'), max_length=50, null=True, blank=True)
    # Отчество
    middle_name = models.CharField(_('Отчество'), max_length=50, null=True, blank=True)
    # Фамилия
    last_name = models.CharField(_('Фамилия'), max_length=50, null=True, blank=True)
    # Аватарка
    avatar = models.ImageField(upload_to=image_file_name)
    # Статус пользователя
    role = models.IntegerField(choices=ROLE_CHOICES, default=ROLE_USER)

    def __str__(self):
        return 'Профиль: {}'.format(self.user.email)
