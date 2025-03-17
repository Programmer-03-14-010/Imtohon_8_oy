from django.db import models
from django.conf import settings

from app_conf.models.students_model import *


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="groups")
    name = models.CharField(max_length=100)
    students = models.ManyToManyField('app_conf.StudentModel', related_name='group_students', blank=True)
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='teacher_groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.course.name})"


class GroupStudent(models.Model):
    student = models.ForeignKey('StudentModel', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    enrollment_date = models.DateField()



class Homework(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="homeworks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class HomeworkSubmission(models.Model):
    homework = models.ForeignKey('Homework', on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Submission by {self.student.username} for {self.homework.title}"

class HomeworkReview(models.Model):
    submission = models.ForeignKey('HomeworkSubmission', on_delete=models.CASCADE, related_name="reviews")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    feedback = models.TextField()
    grade = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.submission}"


class Subject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class TableType(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Table(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="tables")
    table_type = models.ForeignKey(TableType, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class MonthModel(models.Model):
    name = models.CharField(max_length=50)
    number = models.IntegerField(unique=True)

    def __str__(self):
        return self.name