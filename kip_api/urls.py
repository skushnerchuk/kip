from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views.courses import (
    CourseSignupView, CoursesListView, CourseDetailView
)
from .views.user import (
    CreateUserView, ConfirmEmailView, LoginView, UserDetailView,
)

urlpatterns = [
    path('auth/register/', CreateUserView.as_view(), name='register'),
    path('auth/confirm_email/<str:user>/<str:token>', ConfirmEmailView.as_view(), name='confirm_email'),
    path('auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('course/signup/', CourseSignupView.as_view(), name='course_signup'),
    path('course/', CoursesListView.as_view(), name='course_list'),
    path('course/<str:pk>/', CourseDetailView.as_view(), name='course_detail'),

    path('user/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
]
