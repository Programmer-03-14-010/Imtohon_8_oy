from django.urls import path, include
from app_conf.views import *
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="This is the API documentation for our Django project",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path('api/admins/', AdminListCreateApi.as_view(), name='admin-list'),
    path('api/admins/<int:id>/', AdminDetailApi.as_view(), name='admin-detail'),
]
