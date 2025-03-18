from importlib.resources._common import _

from django.contrib import admin

from .models.students_model import *

from .models.staffs_model import *

from .models.admin_model import *

from .models.User_model import *

admin.site.register(AdminModel)


# @admin.register(GroupModel)
# class GroupModelAdmin(admin.ModelAdmin):
#   list_display = ('name', 'teacher', 'course', 'enrolled_students_count', 'active_students_count', 'graduated_students_count')
#   list_filter = ('teacher', 'course')
#   search_fields = ('name', 'course', 'teacher__first_name', 'teacher__last_name')
#   list_per_page = 25
#   ordering = ('name',)
#   readonly_fields = ('enrolled_students_count', 'active_students_count', 'graduated_students_count')
#
#   fieldsets = (
#       (_('Asosiy ma\'lumotlar'), {
#           'fields': ('name', 'teacher', 'course')
#       }),
#       (_('Statistika'), {
#           'fields': ('enrolled_students_count', 'active_students_count', 'graduated_students_count')
#       }),
#   )
#
#   def enrolled_students_count(self, obj):
#       return StudentModel.objects.filter(group=obj, status='enrolled').count()
#   enrolled_students_count.short_description = _('Ro\'yxatdan o\'tganlar')
#
#   def active_students_count(self, obj):
#       return StudentModel.objects.filter(group=obj, status='active').count()
#   active_students_count.short_description = _('O\'qiyotganlar')
#
#   def graduated_students_count(self, obj):
#       return StudentModel.objects.filter(group=obj, status='graduated').count()
#   graduated_students_count.short_description = _('Bitirganlar')
#
#   def get_queryset(self, request):
#       qs = super().get_queryset(request)
#       return qs.prefetch_related('students')


# @admin.register(StudentsStatusModel)
# class StudentStatusModelAdmin(admin.ModelAdmin):
#     list_display = ('student', 'group', 'enrollment_date', 'status', 'graduation_date')
#     list_filter = ('status', 'enrollment_date', 'graduation_date')
#     search_fields = ('student__first_name', 'student__last_name', 'group__name')
#     list_per_page = 25
#     ordering = ('-enrollment_date',)
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.select_related('student', 'group')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']

@admin.register(Group)
class CourseGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'created_at', 'updated_at']
    search_fields = ['name', 'course__name']

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'due_date', 'created_at', 'updated_at']
    search_fields = ['title']

@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'homework', 'submitted_at', 'updated_at']
    search_fields = ['student__username', 'homework__title']

@admin.register(HomeworkReview)
class HomeworkReviewAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'submission', 'grade', 'created_at', 'updated_at']
    search_fields = ['teacher__username', 'submission__student__username']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'created_at', 'updated_at']
    search_fields = ['name', 'course__name']

@admin.register(TableType)
class TableTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'table_type', 'created_at', 'updated_at']
    search_fields = ['title', 'subject__name']


# @admin.register(WorkerModel)
# class WorkerAdmin(admin.ModelAdmin):
#     list_display = ('user', 'created', 'updated', 'get_departments', 'get_courses')
#     search_fields = ('user__phone', 'descriptions')
#     list_filter = ('created', 'updated')
#     filter_horizontal = ('departments', 'course')
#     list_per_page = 25
#     ordering = ('-created',)
#
#     def get_departments(self, obj):
#         return ", ".join([dept.title for dept in obj.departments.all()])
#     get_departments.short_description = 'Departments'
#
#     def get_courses(self, obj):
#         return ", ".join([course.title for course in obj.course.all()])
#     get_courses.short_description = 'Courses'
#

# @admin.register(LevelModel)
# class LevelAdmin(admin.ModelAdmin):
#     list_display = ('title',)
#     search_fields = ('title',)
#
# @admin.register(PartModel)
# class PartAdmin(admin.ModelAdmin):
#     list_display = ('title', 'course', 'level')
#     search_fields = ('title', 'course__title', 'level__title')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'full_name', 'is_active', 'is_staff', 'is_admin')
    search_fields = ('phone', 'full_name')
    list_filter = ('is_active', 'is_staff', 'is_admin')

# @admin.register(CourseModel)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ('title', 'descriptions')

# @admin.register(AdminModel)
# class AdminAdmin(admin.ModelAdmin):
#     list_display = ('phone_number', 'full_name', 'is_staff', 'is_super', 'is_active')
#     search_fields = ('phone_number', 'full_name')

@admin.register(DepartmentModel)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    search_fields = ('title',)

# @admin.register(SubjectModel)
# class SubjectAdmin(admin.ModelAdmin):
#     list_display = ('title', 'descriptions')

@admin.register(TeacherModel)
class TeacherAdmin(admin.ModelAdmin):
     list_display = ( 'created', 'updated')
     search_fields = ('user__phone', 'descriptions')
     filter_horizontal = ('departments', 'course')

# @admin.register(TeacherWorkerModel)
# class TeacherWorkerAdmin(admin.ModelAdmin):
#     list_display = ['id', 'full_name', 'user', 'get_groups']
#     list_filter = ['user__is_teacher']
#     search_fields = ['full_name', 'user__username']
#
#     def get_groups(self, obj):
#         return ", ".join([group.name for group in obj.groups.all()])
#     get_groups.short_description = 'Groups'
#
#     class GroupInline(admin.TabularInline):
#         model = GroupModel
#         extra = 1
#
#     inlines = [GroupInline]

@admin.register(StudentGroupModel)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'start_date', 'end_date', 'active')
    list_filter = ('course', 'active')
    search_fields = ('title',)

@admin.register(StudentModel)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('created', 'updated', 'is_line')
    list_filter = ('is_line',)
    search_fields = ('user__phone',)

# @admin.register(CourseGroup)
# class CourseGroupAdmin(admin.ModelAdmin):
#     list_display = ('name', 'course', 'created_at', 'updated_at')
#     search_fields = ('name', 'course__name')
#     list_filter = ('course', 'created_at')
#     filter_horizontal = ('students', 'teachers')

# @admin.register(TopicModel)
# class TopicAdmin(admin.ModelAdmin):
#     list_display = ('title', 'course', 'is_active')
#     search_fields = ('title',)
#     list_filter = ('is_active',)
#

@admin.register(ParentModel)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'student', 'phone')
    search_fields = ('name', 'surname', 'phone')

# @admin.register(DayModel)
# class DayAdmin(admin.ModelAdmin):
#     list_display = ('title', 'descriptions')
#
# @admin.register(RoomModel)
# class RoomAdmin(admin.ModelAdmin):
#     list_display = ('title', 'descriptions')


@admin.register(PaymentMonth)
class PaymentMonthAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(PaymentType)
class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'month', 'type', 'amount')
    list_filter = ('month', 'type')
    search_fields = ('month__name', 'type__name')

@admin.register(AttendanceModel)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'get_group', 'level')

    def get_group(self, obj):
        return obj.group.name
    get_group.short_description = 'Group'

# @admin.register(TableModel)
# class TableAdmin(admin.ModelAdmin):
#     list_display = ('start_time', 'finish_time', 'room', 'type')
#     list_filter = ('type',)
#
# @admin.register(TableTypeModel)
# class TableTypeAdmin(admin.ModelAdmin):
#     list_display = ('title', 'descriptions')

