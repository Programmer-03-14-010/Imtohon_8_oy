from django.urls import path
from ..views import *

urlpatterns = [
    path('teachers/', TeacherAPIView.as_view(), name='teacher-list-create'),
    path('teachers/groups/<int:id>/', TeacherGroupsAPIView.as_view(), name='teacher-detail'),
    path('teacher/group/<int:group_id>/', TeacherGroupDetailAPIView.as_view(), name='teacher_group_detail'),
    path('group/<int:group_id>/monthly-data/', GroupMonthlyDataAPIView.as_view(), name='group_monthly_data'),
    path('group/<int:group_id>/students/', GroupStudentsAPIView.as_view(), name='group_students'),
]
