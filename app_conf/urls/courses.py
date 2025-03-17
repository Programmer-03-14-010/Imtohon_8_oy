from django.urls import path
from ..views import *

app_name = 'courses'

urlpatterns = [
    path('courses/', CourseListCreateView.as_view(), name='courses_list_create'),
    path('courses/<int:id>/', CourseDetailView.as_view(), name='courses_detail'),
    path('courses/<int:id>/delete_course/', CourseDetailView.as_view(), name='delete_course'),
    path('courses/<int:id>/update_course/', CourseDetailView.as_view(), name='update_course'),

    path('courses_groups/', GroupsListCreateView.as_view(), name='course_groups_list_create'),
    path('courses_groups/<int:id>/', GroupsDetailView.as_view(), name='course_groups_detail'),
    path('courses_groups/add_student/', GroupsAddStudentView.as_view(), name='add_student'),
    path('courses_groups/add_teacher/', GroupsAddTeacherView.as_view(), name='add_teacher'),
    path('courses_groups/delete_group/', GroupsDetailView.as_view(), name='delete_group'),
    path('courses_groups/remove_student/', GroupsRemoveStudentView.as_view(), name='remove_student'),
    path('courses_groups/remove_teacher/<int:id>/', GroupsRemoveTeacherView.as_view(), name='remove_teacher'),
    path('courses_groups/<int:id>/update_group/', GroupsDetailView.as_view(), name='update_group'),

    path('courses_homeworks/', HomeworkListCreateView.as_view(), name='homeworks_list_create'),
    path('courses_homeworks/<int:id>/', HomeworkDetailView.as_view(), name='homeworks_detail'),
    path('courses_homeworks/<int:id>/delete_homework/', HomeworkDetailView.as_view(), name='delete_homework'),
    path('courses_homeworks/<int:id>/update_homework/', HomeworkDetailView.as_view(), name='update_homework'),

    path('courses_homework_submissions/', HomeworkSubmissionListCreateView.as_view(), name='submissions_list_create'),
    path('courses_homework_submissions/<int:id>/', HomeworkSubmissionDetailView.as_view(), name='submissions_detail'),
    path('courses_homework_submissions/<int:id>/delete_homework_submission/', HomeworkSubmissionDetailView.as_view(), name='delete_submission'),
    path('courses_homework_submissions/<int:id>/update_homework_submission/', HomeworkSubmissionDetailView.as_view(), name='update_submission'),

    path('courses_homework_reviews/', HomeworkReviewListCreateView.as_view(), name='reviews_list_create'),
    path('courses_homework_reviews/<int:id>/', HomeworkReviewDetailView.as_view(), name='reviews_detail'),
    path('courses_homework_reviews/<int:id>/delete_homework_review/', HomeworkReviewDetailView.as_view(), name='delete_review'),
    path('courses_homework_reviews/<int:id>/update_homework_review/', HomeworkReviewDetailView.as_view(), name='update_review'),

    path('courses_subjects/', SubjectListCreateView.as_view(), name='subjects_list_create'),
    path('courses_subjects/<int:id>/', SubjectDetailView.as_view(), name='subjects_detail'),
    path('courses_subjects/<int:id>/delete_subject/', SubjectDetailView.as_view(), name='delete_subject'),
    path('courses_subjects/<int:id>/update_subject/', SubjectDetailView.as_view(), name='update_subject'),

    path('courses_table_types/', TableTypeListCreateView.as_view(), name='table_types_list_create'),
    path('courses_table_types/<int:id>/', TableTypeDetailView.as_view(), name='table_types_detail'),
    path('courses_table_types/<int:id>/delete_tabletype/', TableTypeDetailView.as_view(), name='delete_table_type'),
    path('courses_table_types/<int:id>/update_tabletype/', TableTypeDetailView.as_view(), name='update_table_type'),

    path('courses_tables/', TableListCreateView.as_view(), name='tables_list_create'),
    path('courses_tables/<int:id>/', TableDetailView.as_view(), name='tables_detail'),
    path('courses_tables/<int:id>/delete_table/', TableDetailView.as_view(), name='delete_table'),
    path('courses_tables/<int:id>/update_table/', TableDetailView.as_view(), name='update_table'),
]