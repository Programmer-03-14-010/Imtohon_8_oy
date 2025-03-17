from django.urls import path
from ..views import (
    ChangePasswordView, LoginView, LogoutView, MeView,
    ResetPasswordView, SetNewPasswordView, TokenRefreshView,
    VerifyOtpView
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Auth API Documentation",
        default_version='v1',
        description="Authentication API for the Django project",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
]