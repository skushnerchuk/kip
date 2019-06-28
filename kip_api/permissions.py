from rest_framework.permissions import BasePermission


class IsEmailConfirmed(BasePermission):
    """
    Доступ только для пользователей с подтвержденной почтой
    """

    message = "Для этого действия вы должны иметь подтвержденную электронную почту"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.email_confirmed)
