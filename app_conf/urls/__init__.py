from django.urls import path
from ..views import (
    AttendanceAPIView,
    AttendanceGetPIView,
    AttendancePUTAIView,
    AttendanceDelatePIView,
)

urlpatterns = [
    path('Create/attendance', AttendanceAPIView.as_view(), name='attendance-create'),
    path('Get/<int:pk>/attendance', AttendanceGetPIView.as_view(), name='attendance-get'),
    path('Put/<int:pk>/attendance', AttendancePUTAIView.as_view(), name='attendance-put'),
    path('Delate/<int:pk>/attendance', AttendanceDelatePIView.as_view(), name='attendance-delate'),
]