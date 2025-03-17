from django.db import models

from app_conf.models.courses_model import Course
from app_conf.models.User_model import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Foydalanuvchi nomi kiritilishi shart")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class AdminModel(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_super = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    descriptions = models.TextField(blank=True, null=True)

class WorkerModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    departments = models.ManyToManyField('DepartmentModel', related_name='workers')
    course = models.ManyToManyField(Course, related_name='workers')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.user.phone


class DepartmentModel(models.Model):
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    descriptions = models.TextField(blank=True, null=True)

class LevelModel(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class PartModel(models.Model):
    title = models.CharField(max_length=100)
    descriptions = models.TextField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.ForeignKey(LevelModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.course.title} - {self.level.title}"

class TableModel(models.Model):
    start_time = models.TimeField()
    finish_time = models.TimeField()
    room = models.CharField(max_length=50)
    descriptions = models.TextField(blank=True, null=True)
    type = models.ForeignKey('TableTypeModel', on_delete=models.CASCADE)

class TableTypeModel(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.TextField(blank=True, null=True)