from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status

from kip_api.mixins import ObjectExistMixin, EmailMixin
from kip_api.models.courses import CourseGroup, Participation, UserLessons
from kip_api.utils import APIException

User = get_user_model()


class CourseService(ObjectExistMixin, EmailMixin):
    """
    Слой логики по работе с курсами, группами и уроками
    """

    def enroll(self, pk, group_id):
        """
        Регистрация пользователя в группе курса
        При регистрации пользователя мы автоматически формируем для него таблицу расписания.
        Флаги оплаты проставляются после оплаты части курса или курса целиком
        Минимальная единица оплаты курса - занятие

        Записываться на курс можно только если пользователь в настоящее время не
        состоит в группе курса, которая не закончила обучение. Повторно проходить курс
        мы разрешаем.

        Частным случаем является перевод пользователя из группы в группу, и это решается
        через административную панель

        :param pk: идентификатор пользователя
        :param group_id: индектификатор группы
        """

        # Возникновение 404 тут маловероятно, но все-таки возможно
        user = get_object_or_404(User, pk=pk)
        # Не разрешаем записываться на курс повторно, если пользователь состоит в открытой группе
        # TODO Уточнить условие отбора, такой поиск не работает как надо
        if self.object_exists(Participation, {'user': pk, 'group': group_id, 'closed': False}):
            raise APIException('Вы уже записаны на этот курс', status.HTTP_400_BAD_REQUEST)
        group = get_object_or_404(CourseGroup, pk=group_id)
        # Получаем все уроки для данной группы курса
        lessons = group.lesson_set.all()
        with transaction.atomic():
            # Добавляем пользователя в группу
            user.groups.add(group_id, pk)
            user.save()
            # Формируем для него расписание
            for l in lessons:
                UserLessons.objects.create(
                    lesson_id=l.pk,
                    user_id=pk
                ).save()
