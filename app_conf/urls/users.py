from django.urls import path
from ..views import *

urlpatterns = [
    path('users/', UserListView.as_view(), name='users_list'),
    path('users/create-superuser/', CreateSuperUserView.as_view(), name='users_create_superuser'),
    path('users/create-student/', CreateStudentView.as_view(), name='users_create_student'),
    path('users/create-teacher/', CreateTeacherView.as_view(), name='users_create_teacher'),
    path('users/create-parent/', CreateParentView.as_view(), name='users_create_parent'),
    path('users/create/', UserAPI.as_view(), name='teacher-list-create'),
    path('users/<int:id>/', UserListApi.as_view(), name='teacher-detail'),
]