from email.policy import default

from django.db import models
from django.conf import settings

from app_conf.models.courses_model import Course
from app_conf.models.courses_model import *
from app_conf.models.staffs_model import *
from app_conf.models.admin_model import *



class StudentGroupModel(models.Model):
    title = models.CharField(max_length=255, unique=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, default=1)
    teacher = models.ManyToManyField(TeacherModel, related_name='teaching_groups')
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.CharField(max_length=15, blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    descriptions = models.TextField(blank=True, null=True)
    table = models.ForeignKey('Table', on_delete=models.CASCADE)

    enrollment_date = models.DateField(null=True, blank=True)
    graduation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('enrolled', 'Enrolled'), ('active', 'Active'), ('graduated', 'Graduated')])



class StudentModel(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='student_groups')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_line = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)
    enrollment_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[('enrolled', 'Enrolled'), ('active', 'Active'), ('graduated', 'Graduated')],
        default='enrolled'
    )
    graduation_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('registered', 'Registered'),
        ('studying', 'Studying'),
        ('graduated', 'Graduated'),
    )
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    date_joined = models.DateField()

    def __str__(self):
        return f"{self.student} - {self.course} ({self.status})"


# class StudentsStatusModel(models.Model):
#     student = models.ForeignKey('StudentModel', on_delete=models.CASCADE)
#     group = models.ForeignKey(GroupModel, on_delete=models.CASCADE, related_name='students_groups')
#     enrollment_date = models.DateField()
#     status = models.CharField(
#         max_length=20,
#         choices=[('enrolled', 'Enrolled'), ('active', 'Active'), ('graduated', 'Graduated')],
#         default='enrolled'
#     )
#     graduation_date = models.DateField(null=True, blank=True)
#
#     def __str__(self):
#         return f"{self.student} - {self.group}"
#
#     class Meta:
#         verbose_name = "Student_Status"
#         verbose_name_plural = "Student_Statuses"

class ParentModel(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE)
    address = models.TextField()
    descriptions = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20)


class PaymentMonth(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class PaymentType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Payment(models.Model):
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE)
    month = models.ForeignKey(PaymentMonth, on_delete=models.CASCADE)
    type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.student} - {self.type} - {self.amount}"


class AttendanceModel(models.Model):
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE)
    group = models.ForeignKey('app_conf.Group', on_delete=models.CASCADE)
    level = models.CharField(max_length=50)
    date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class AttendanceStatus(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
