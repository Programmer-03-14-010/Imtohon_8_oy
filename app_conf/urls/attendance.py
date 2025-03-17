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
    path('create/attendance', AttendanceAPIView.as_view(), name='attendance-create'),
    path('get/<int:id>/attendance', AttendanceGetPIView.as_view(), name='attendance-get'),
    path('put/<int:pk>/attendance', AttendancePUTAIView.as_view(), name='attendance-put'),
    path('satus/delete/<int:pk>/attendance', AttendanceDelatePIView.as_view(), name='attendance-delate'),
    path('status/attendance', AttendanceStatusAPIView.as_view(), name='attendance-status-create'),
    path('status/get/<int:pk>/attendance', AttendanceStatusGetAPIView.as_view(), name='attendance-status-get'),
    path('status/put/<int:pk>/attendance', AttendanceStatusPutAPIView.as_view(), name='attendance-status-put'),
    path('status/delete/<int:pk>/attendance', AttendanceStatusDeleteAPIView.as_view(), name='attendance-status-delete'),
]


"""

from tkinter.font import names

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from app_conf.views import UserAPI

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

router = DefaultRouter()


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),


    path('users/', UserAPI.as_view(), name='user-list'),
    path('workers/', WorkerAPIView.as_view(), name='worker-list'),
    path('students/', StudentApiView.as_view(), name='student-detail'),
    path('student-stats/', StudentStatusApiView.as_view(), name='student-stats'),
    path('students_get_data/', StudentListBy.as_view(), name='student_list_by_ids'),
    path('groups_get_data/', GroupListBy.as_view(), name='group_list_by_ids'),
    path('course/', CourseModelAPIView.as_view(), name='course-api'),
    path('payments/', PaymentListApi.as_view(), name='payment-list'),
    path('tables/<int:id>/', TableDetailApi.as_view(), name='table-detail'),
    path('table-types/<int:id>/delete/', TableTypeDeleteApi.as_view(), name='table-type-delete'),
    path('departments/', DepartmentListCreateAPIView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', DepartmentDetailAPIView.as_view(), name='department-detail'),
    path('parents/', ParentListCreateAPIView.as_view(), name='parent-list-create'),
    path('parents/<int:pk>/', ParentDetailAPIView.as_view(), name='parent-detail'),
    path('groups/', GroupModelAPIView.as_view(), name='group-api'),
    path('group_get/', GroupApi.as_view(), name='group-detail'),
    path('teachers/', TeacherApiView.as_view(), name='teacher-api'),
    path('teacher-groups/<int:teacher_id>/', TeacherGroupsApiView.as_view(), name='teacher-groups'),
    path('levels/', LevelListCreateAPIView.as_view(), name='level-list'),
    path('levels/<int:pk>/', LevelDetailAPIView.as_view(), name='level-detail'),
    path('parts/', PartListCreateAPIView.as_view(), name='part-list'),
    path('parts/<int:pk>/', PartDetailAPIView.as_view(), name='part-detail'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include(router.urls)),
]
"""