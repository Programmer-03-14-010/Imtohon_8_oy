from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('auth/', include('app_conf.urls.auth')),
    path('admin/', admin.site.urls),
    path('attendance/', include('app_conf.urls.attendance')),
    path('admin/', include('app_conf.urls.admin')),
    path('courses/', include('app_conf.urls.courses')),
    path('payments/', include('app_conf.urls.payments')),
    path('students/', include('app_conf.urls.students')),
    path('parents/', include('app_conf.urls.parents')),
    path('teachers/', include('app_conf.urls.teachers')),
    path('users/', include('app_conf.urls.users')),
    #path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]