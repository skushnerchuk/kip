from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views.courses import (
    CourseSignupView, UserGroupsView, CourseGroupScheduleView, CourseListAllView
)
from .views.user import (
    CreateUserView, ConfirmEmailView, LoginView, UserDetailView, LogoutView,
    UserUpdateView, UserUpdateAvatarView
)

urlpatterns = [
    # Работа с пользователями

    # Регистрация
    path('auth/register/', CreateUserView.as_view(), name='register'),
    # Подтверждение электронной почты (приходят по ссылке из письма)
    path('auth/confirm_email/<str:user>/<str:token>', ConfirmEmailView.as_view(), name='confirm_email'),
    # Авторизация
    path('auth/login/', LoginView.as_view(), name='login'),
    # Выход из системы
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    # Обновление токенв
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Проверка токенов
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # Получение сведений о пользователе
    path('user/', UserDetailView.as_view(), name='user_detail'),
    # Обновление сведений о пользователе
    path('user/update/', UserUpdateView.as_view(), name='user_update'),
    # Загрузка или удаление аватара пользователя
    path('user/update/avatar/', UserUpdateAvatarView.as_view(), name='user_update_avatar'),
    # Просмотр курсов, на которые записан пользователь
    path('user/groups/', UserGroupsView.as_view(), name='user_courses'),

    # Работа с курсами

    # Просмотр всех доступных курсов
    path('course/all/', CourseListAllView.as_view(), name='course_view_all'),
    # Запись пользователя на курс
    path('course/signup/', CourseSignupView.as_view(), name='course_signup'),
    # Просмотр расписания группы курса
    path('course/<str:group_id>/schedule/', CourseGroupScheduleView.as_view(), name='group_schedule'),
    #
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
