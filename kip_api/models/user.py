from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .courses import CourseGroup

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

    # Следует помнить, что пользователь не может участвовать одновременно более чем в одной группе курса
    groups = models.ManyToManyField(CourseGroup, blank=True)

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
