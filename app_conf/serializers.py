from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from rest_framework import serializers

from .models import Subject, Homework
from .models.students_model import *

from .models.staffs_model import *

from  .models.admin_model import *


User = get_user_model()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        user = authenticate(username=data['phone'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Noto‘g‘ri foydalanuvchi nomi yoki parol")
        return data


class LogoutSerializer(serializers.Serializer):
    pass

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class SetNewPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)

    class Meta:
        ref_name = "CustomTokenRefreshSerializer"


class VerifyOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    otp_code = serializers.CharField(max_length=6, required=True)


class StudentRequestSerializer(serializers.Serializer):
    student_ids = serializers.ListField(child=serializers.IntegerField())



class AttendanceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceStatus
        fields = '__all__'

class GroupRequestSerializer(serializers.Serializer):
    group_ids = serializers.ListField(child=serializers.IntegerField())


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'full_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'is_staff', 'is_admin']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class UserAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class CourseGroupSerializer(serializers.ModelSerializer):
    students = UserSerializer(many=True, read_only=True)
    teachers = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = '__all__'

class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = '__all__'

class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = HomeworkSubmission
        fields = '__all__'

class HomeworkReviewSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = HomeworkReview
        fields = '__all__'

class DateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        """ start_date end_date'dan katta bo‘lmasligini tekshiramiz """
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date end date'dan katta bo‘lishi mumkin emas.")
        return data



class CourseRegistrationSerializer(serializers.Serializer):
    course = serializers.CharField()
    student_count = serializers.IntegerField()

class StudentsByRegistrationSerializer(serializers.Serializer):
    registered_by_course = CourseRegistrationSerializer(many=True)
    studying = serializers.IntegerField()
    compleated = serializers.IntegerField()


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class TableTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableType
        fields = '__all__'

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'

class AddUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    group_id = serializers.IntegerField()


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherModel
        fields = ['id', 'departments', 'course', 'created', 'updated', 'descriptions']

    def create(self, validated_data):
        validated_data.pop('user', None)
        return super().create(validated_data)

class TeacherGroupSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=288)

    class Meta:
        model = TeacherModel
        fields = '__all__'


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerModel
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentModel
        fields = '__all__'



class GroupStatsSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source='course_field_name')
    enrolled_count = serializers.SerializerMethodField()
    active_count = serializers.SerializerMethodField()
    graduated_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'course', 'enrolled_count', 'active_count', 'graduated_count']


    def get_enrolled_count(self, obj):
        date1 = self.context['date1']
        date2 = self.context['date2']
        return StudentModel.objects.filter(
            group=obj,
            enrollment_date__range=[date1, date2],
            status='enrolled'
        ).count()

    def get_active_count(self, obj):
        date1 = self.context['date1']
        date2 = self.context['date2']
        return StudentModel.objects.filter(
            group=obj,
            enrollment_date__range=[date1, date2],
            status='active'
        ).count()

    def get_graduated_count(self, obj):
        date1 = self.context['date1']
        date2 = self.context['date2']
        return StudentModel.objects.filter(
            group=obj,
            graduation_date__range=[date1, date2],
            status='graduated'
        ).count()



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGroupModel
        fields = ['id', 'course', 'price', 'descriptions']


# class TeacherGroupSerializer(serializers.ModelSerializer):
#     groups = GroupsSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = TeacherWorkerModel
#         fields = ['id', 'full_name', 'groups']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentModel
        fields = ['id', 'group', 'course', 'is_line', 'descriptions', 'enrollment_date', 'status']

    def create(self, validated_data):
        """Talaba yaratish"""

        # 📌 `course` ni tekshirish
        if 'course' not in validated_data:
            raise serializers.ValidationError({"course": "Kurs maydoni talab qilinadi."})

        return StudentModel.objects.create(**validated_data)


class UserAndStudentSerializer(serializers.Serializer):
    user = UserSerializer()
    student = StudentSerializer()


class UserAndWorkerSerializer(serializers.Serializer):
    user = UserSerializer()
    worker = WorkerSerializer()


class UserAndTeacherSerializer(serializers.Serializer):
    user = UserSerializer()
    teacher = TeacherSerializer()

class UserAndAdminSerializer(serializers.Serializer):
    user = UserSerializer()
    admin = AdminSerializer()


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentModel
        fields = '__all__'

class PaymentMonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMonth
        fields = '__all__'

class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'



class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceModel
        fields = '__all__'


class GroupStatsSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source='course.name')
    enrolled_count = serializers.SerializerMethodField()
    active_count = serializers.SerializerMethodField()
    graduated_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'course', 'enrolled_count', 'active_count', 'graduated_count']

    def get_enrolled_count(self, obj):
        date1 = self.context['date1']
        date2 = self.context['date2']
        return StudentModel.objects.filter(
            group=obj,
            enrollment_date__range=[date1, date2],
            status='enrolled'
        ).count()

    def get_active_count(self, obj):
        date1 = self.context['date1']
        date2 = self.context['date2']
        return StudentModel.objects.filter(
            group=obj,
            enrollment_date__range=[date1, date2],
            status='active'
        ).count()

    def get_graduated_count(self, obj):
        date1 = self.context['date1']
        date2 = self.context['date2']
        return StudentModel.objects.filter(
            group=obj,
            graduation_date__range=[date1, date2],
            status='graduated'
        ).count()

class StudentStatusSerializer(serializers.ModelSerializer):
    enrolled_count = serializers.SerializerMethodField()

    class Meta:
        model = StudentModel
        fields = ('id', 'status', 'enrolled_count')

    def get_enrolled_count(self, obj):
        date1 = self.context.get('date1')
        date2 = self.context.get('date2')

        if not date1 or not date2:
            return 0

        return StudentModel.objects.filter(
            created__range=[date1, date2]
        ).count()


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelModel
        fields = '__all__'


class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartModel
        fields = '__all__'


