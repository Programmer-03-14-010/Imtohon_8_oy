from django.urls import path

from app_conf.views import *

app_name = 'students'

urlpatterns = [
    path('students/create/', StudentAPIView.as_view(), name='student-create'),
    path('students/create/<int:id>/students', StudentDetailAPIView.as_view(), name='student-detail'),
    path('student-status/', StudentStatusApiView.as_view(), name='student-stats'),
    path('student-page/', StudentListView.as_view(), name='student-pagination'),
    path('student-ids/', StudentIDSView.as_view(), name='student-ids'),
    path('student/homework/', StudentHomeworkAPIView.as_view(), name='student_homework'),
    path('student/groups/', StudentGroupsAPIView.as_view(), name='student_groups'),
    path('student/attendance/', StudentAttendanceAPIView.as_view(), name='student_attendance'),
    path('student/group-list/', StudentGroupListAPIView.as_view(), name='student_group_list'),

]



#student uy vazifalarini kora olishi
#student guruhlarini kora olishi
#student yo'qlamalarini korish har bir poginatsiyada 1 oy korsatish kerak
#student ozining 1ta guruhidagi ro'yxatini korish
#teacher ozining guruhlari royxatlarini korish, guruhni ustiga bosilganda usha guruh haqida ma'lumot chiqish
#guruh qachon boshlangani, va har bir oy uchun malumotlarni chiqarish paginatsiyada, har birida 30 yoki 31 ta bolishi kerak
#guruhga tegishli studentlarnining ma'lumotlarini olish
