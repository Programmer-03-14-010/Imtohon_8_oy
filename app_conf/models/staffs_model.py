from django.db import models


from app_conf.models.User_model import User
from app_conf.models.students_model import Course


class SubjectModel(models.Model):
    title = models.CharField(max_length=255)
    descriptions = models.TextField(blank=True, null=True)




class TopicModel(models.Model):
    title = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.RESTRICT)
    is_active = models.BooleanField(default=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title





class TeacherWorkerModel(models.Model):
    full_name = models.CharField(max_length=255)
    course = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.full_name

class TeacherModel(models.Model):
    full_name = models.CharField(max_length=255)
    groups = models.ManyToManyField('Group', related_name="teacher_groups")
    departments = models.ManyToManyField('DepartmentModel', related_name='teachers')
    course = models.ManyToManyField('Course', related_name="teachers")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    descriptions = models.CharField(max_length=500, null=True, blank=True)




class DayModel(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title

class RoomModel(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title
