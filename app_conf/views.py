import random
from collections import  Counter
from datetime import  datetime
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import permissions

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password

from rest_framework.authentication import TokenAuthentication

from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from django.contrib.auth import authenticate, login, logout
from drf_yasg import openapi
from fastapi import FastAPI


from django.http import Http404
from django.db.utils import IntegrityError
from rest_framework.exceptions import ValidationError

from .models.students_model import *

from .models.staffs_model import *

from  .models.admin_model import *

from .models.User_model import *

app = FastAPI()




class ChangePasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Foydalanuvchi parolini o‘zgartirish uchun POST so‘rov.",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(description="Parol muvaffaqiyatli o‘zgartirildi"),
            400: openapi.Response(description="Xato: Eski parol noto‘g‘ri yoki ma’lumotlar noto‘g‘ri"),
            401: openapi.Response(description="Tizimga kirmagan")
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not check_password(serializer.validated_data['old_password'], user.password):
                return Response({"error": "Eski parol noto‘g‘ri"}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Parol muvaffaqiyatli o‘zgartirildi"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Foydalanuvchini autentifikatsiya qilish uchun POST so‘rov.",
        request_body=LoginSerializer,
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['phone'], password=serializer.validated_data['password'])
            if user:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
        return Response({"error": "Login yoki parol xato"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Foydalanuvchini chiqarish uchun POST so‘rov.",
        request_body=LogoutSerializer,
    )
    def post(self, request):
        logout(request)
        return Response({"message": "Muvaffaqiyatli chiqish qilindi"}, status=status.HTTP_200_OK)


class MeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Foydalanuvchi haqidagi ma’lumotlarni olish uchun GET so‘rov.",
    )
    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    @swagger_auto_schema(
        operation_description="Parolni tiklash uchun OTP kod yuborish uchun POST so‘rov.",
        request_body=ResetPasswordSerializer,
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.filter(email=serializer.validated_data['email']).first()
            if user:
                otp = random.randint(100000, 999999)
                user.otp_code = str(otp)
                user.save()
                print(f"Foydalanuvchi {user.username} uchun OTP kod: {otp}")
                return Response({"message": "OTP kod terminalda ko‘rsatildi"}, status=status.HTTP_200_OK)
            return Response({"error": "Foydalanuvchi topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Yangi parolni o‘rnatish uchun POST so‘rov.",
        request_body=SetNewPasswordSerializer,
    )
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user and user.otp_code == request.data.get('token'):
                user.set_password(serializer.validated_data['new_password'])
                user.otp_code = None
                user.save()
                return Response({"message": "Parol muvaffaqiyatli o‘zgartirildi"}, status=status.HTTP_200_OK)
            return Response({"error": "Noto‘g‘ri token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    @swagger_auto_schema(
        operation_description="Access tokenni yangilash uchun POST so‘rov.",
        request_body=TokenRefreshSerializer,
    )
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data.get('refresh_token')
            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
                return Response({'access': new_access_token}, status=status.HTTP_200_OK)
            except Exception:
                return Response({"error": "Noto‘g‘ri refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(APIView):
    @swagger_auto_schema(
        operation_description="OTP kodni tekshirish uchun POST so‘rov.",
        request_body=VerifyOtpSerializer,
    )
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.filter(phone_number=serializer.validated_data['phone_number']).first()
            if user and user.otp_code == serializer.validated_data['otp_code']:
                user.otp_code = None
                user.save()
                return Response({"message": "OTP muvaffaqiyatli tasdiqlandi"}, status=status.HTTP_200_OK)
            return Response({"error": "Noto‘g‘ri OTP kod"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Yangi kurs yaratish",
        request_body=CourseSerializer,
        responses={201: CourseSerializer()}
    )
    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CourseDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Bitta kursni olish",
        responses={200: CourseSerializer()}
    )
    def get(self, request, id):
        course = get_object_or_404(Course, id=id)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Kursni yangilash",
        request_body=CourseSerializer,
        responses={200: CourseSerializer()}
    )
    def put(self, request, id):
        course = get_object_or_404(Course, id=id)
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Kursni o‘chirish",
        responses={204: "Kurs o‘chirildi"}
    )
    def delete(self, request, id):
        course = get_object_or_404(Course, id=id)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GroupsListCreateView(APIView):

    @swagger_auto_schema(
        operation_description="Yangi kurs guruhi yaratish",
        request_body=CourseGroupSerializer,
        responses={201: CourseGroupSerializer()}
    )
    def post(self, request):
        serializer = CourseGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupsGetView(APIView):
    @swagger_auto_schema(
        operation_description="Barcha kurs guruhlarini olish",
        responses={200: CourseGroupSerializer(many=True)}
    )
    def get(self, request):
        groups = Group.objects.all()
        serializer = CourseGroupSerializer(groups, many=True)
        return Response(serializer.data)


class GroupsDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Bitta kurs guruhini olish",
        responses={200: CourseGroupSerializer()}
    )
    def get(self, request, id):
        group = get_object_or_404(Group, id=id)
        serializer = CourseGroupSerializer(group)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Kurs guruhini yangilash",
        request_body=CourseGroupSerializer,
        responses={200: CourseGroupSerializer()}
    )
    def put(self, request, id):
        group = get_object_or_404(Group, id=id)
        serializer = CourseGroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Kurs guruhini o‘chirish",
        responses={204: "Kurs guruhi o‘chirildi"}
    )
    def delete(self, request, id):
        group = get_object_or_404(Group, id=id)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class GroupsAddStudentView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Guruhga talabani qo'shish",
        request_body=AddUserSerializer,
        responses={200: openapi.Response("Student added"), 400: "Bad Request"},
    )
    def post(self, request):
        serializer = AddUserSerializer(data=request.data)
        if serializer.is_valid():
            group = get_object_or_404(Group, id=serializer.validated_data['group_id'])
            user = get_object_or_404(User, id=serializer.validated_data['user_id'])

            student = StudentModel.objects.filter(user=user).first()
            if not student:
                return Response({"error": "Bu foydalanuvchi talaba sifatida ro‘yxatdan o‘tmagan."},
                                status=status.HTTP_400_BAD_REQUEST)

            group.students.add(student)
            return Response({"status": "Student added"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class GroupsAddTeacherView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Guruhga ustoz qo'shish",
        request_body=AddUserSerializer,
        responses={200: openapi.Response("Teacher added"), 400: "Bad Request"},
    )
    def post(self, request):
        serializer = AddUserSerializer(data=request.data)
        if serializer.is_valid():
            group = get_object_or_404(Group, id=serializer.validated_data['group_id'])

            user = get_object_or_404(User, id=serializer.validated_data['user_id'])

            teacher = get_object_or_404(TeacherModel, id=user.id)
            group.teachers.add(teacher.id)

            return Response({"status": "Teacher added"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupsRemoveStudentView(APIView):
    @swagger_auto_schema(
        operation_description="Guruhdan talabani olib tashlash",
        request_body=AddUserSerializer,
        responses={200: openapi.Response("Student removed"), 400: "Bad Request"},
    )
    def post(self, request, id):
        group = get_object_or_404(Group, id=id)
        serializer = AddUserSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, id=serializer.validated_data['user_id'])
            group.students.remove(user)
            return Response({"status": "Student removed"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupsRemoveTeacherView(APIView):
    @swagger_auto_schema(
        operation_description="Guruhdan ustozni olib tashlash",
        request_body=AddUserSerializer,
        responses={200: openapi.Response("Teacher removed"), 400: "Bad Request"},
    )
    def post(self, request, id):  # <-- ID argumentini qo‘shdik!
        group = get_object_or_404(Group, id=id)
        serializer = AddUserSerializer(data=request.data)

        if serializer.is_valid():
            user = get_object_or_404(User, id=serializer.validated_data['user_id'])

            # User bilan bog‘liq TeacherModel obyektini topamiz
            teacher = TeacherModel.objects.filter(user=user).first()
            if not teacher:
                return Response({"error": "Bu foydalanuvchi o‘qituvchi emas."}, status=status.HTTP_400_BAD_REQUEST)

            # Agar o‘qituvchi guruhda bo‘lsa, uni olib tashlaymiz
            if teacher in group.teachers.all():
                group.teachers.remove(teacher)
                return Response({"status": "Teacher removed"}, status=status.HTTP_200_OK)

            return Response({"error": "Bu o‘qituvchi bu guruhga tegishli emas."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HomeworkListCreateView(APIView):
    @swagger_auto_schema(request_body=HomeworkSerializer, responses={201: HomeworkSerializer})
    def post(self, request):
        serializer = HomeworkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HomeworkDetailView(APIView):
    @swagger_auto_schema(responses={200: HomeworkSerializer})
    def get(self, request, id):
        homework = get_object_or_404(Homework, id=id)
        serializer = HomeworkSerializer(homework)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=HomeworkSerializer, responses={200: HomeworkSerializer})
    def put(self, request, id):
        homework = get_object_or_404(Homework, id=id)
        serializer = HomeworkSerializer(homework, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: 'No Content'})
    def delete(self, request, id):
        homework = get_object_or_404(Homework, id=id)
        homework.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# HomeworkSubmission Views
class HomeworkSubmissionDetailView(APIView):
    @swagger_auto_schema(responses={200: HomeworkSubmissionSerializer(many=True)})
    def get(self, request, id):
        submission = get_object_or_404(HomeworkSubmission, id=id)
        serializer = HomeworkSubmissionSerializer(submission)
        return Response(serializer.data)

class HomeworkSubmissionListCreateView(APIView):
    @swagger_auto_schema(request_body=HomeworkSubmissionSerializer, responses={201: HomeworkSubmissionSerializer})
    def post(self, request):
        serializer = HomeworkSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HomeworkReviewDetailView(APIView):
    @swagger_auto_schema(responses={200: HomeworkReviewSerializer(many=True)})
    def get(self, request, id):
        review = get_object_or_404(HomeworkReview, id=id)
        serializer = HomeworkReviewSerializer(review)
        return Response(serializer.data)

class HomeworkReviewListCreateView(APIView):
    @swagger_auto_schema(request_body=HomeworkReviewSerializer, responses={201: HomeworkReviewSerializer})
    def post(self, request):
        serializer = HomeworkReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubjectListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=SubjectSerializer, responses={201: SubjectSerializer})
    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        subject = get_object_or_404(Subject, id=id)
        serializer = SubjectSerializer(subject)
        return Response(serializer.data)

    def put(self, request, id):
        subject = get_object_or_404(Subject, id=id)
        serializer = SubjectSerializer(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        subject = get_object_or_404(Subject, id=id)
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TableTypeListCreateView(APIView):
    @swagger_auto_schema(
        operation_summary="List all table types",
        operation_description="Retrieve a list of all table types.",
        responses={200: TableTypeSerializer(many=True)}
    )
    def get(self, request):
        table_types = TableType.objects.all()
        serializer = TableTypeSerializer(table_types, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new table type",
        operation_description="Create a new table type with the provided data.",
        responses={201: TableTypeSerializer(), 400: "Bad Request"},
        request_body=TableTypeSerializer
    )
    def post(self, request):
        serializer = TableTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TableTypeDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve a table type",
        operation_description="Get details of a specific table type by ID.",
        responses={200: TableTypeSerializer(), 404: "Not Found"}
    )
    def get(self, request, id):
        table_type = get_object_or_404(TableType, id=id)
        serializer = TableTypeSerializer(table_type)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update a table type",
        operation_description="Update details of a specific table type by ID.",
        responses={200: TableTypeSerializer(), 400: "Bad Request", 404: "Not Found"},
        request_body=TableTypeSerializer
    )
    def put(self, request, id):
        table_type = get_object_or_404(TableType, id=id)
        serializer = TableTypeSerializer(table_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a table type",
        operation_description="Delete a specific table type by ID.",
        responses={204: "No Content", 404: "Not Found"}
    )
    def delete(self, request, id):
        table_type = get_object_or_404(TableType, id=id)
        table_type.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TableListCreateView(APIView):
    @swagger_auto_schema(
        operation_summary="List all tables",
        operation_description="Retrieve a list of all tables.",
        responses={200: TableSerializer(many=True)}
    )
    def get(self, request):
        tables = Table.objects.all()
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new table",
        operation_description="Create a new table with the provided data.",
        responses={201: TableSerializer(), 400: "Bad Request"},
        request_body=TableSerializer
    )
    def post(self, request):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TableDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve a table",
        operation_description="Get details of a specific table by ID.",
        responses={200: TableSerializer(), 404: "Not Found"}
    )
    def get(self, request, id):
        table = get_object_or_404(Table, id=id)
        serializer = TableSerializer(table)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update a table",
        operation_description="Update details of a specific table by ID.",
        responses={200: TableSerializer(), 400: "Bad Request", 404: "Not Found"},
        request_body=TableSerializer
    )
    def put(self, request, id):
        table = get_object_or_404(Table, id=id)
        serializer = TableSerializer(table, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a table",
        operation_description="Delete a specific table by ID.",
        responses={204: "No Content", 404: "Not Found"}
    )
    def delete(self, request, id):
        table = get_object_or_404(Table, id=id)
        table.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminListCreateApi(APIView):
    @swagger_auto_schema(
        operation_description="Yangi admin yaratish",
        request_body=UserAndAdminSerializer,
        responses={
            201: UserAndAdminSerializer(),
            400: "Xato",
        }
    )
    def post(self, request):
        serializer = UserAndAdminSerializer(data=request.data)
        if serializer.is_valid():
            admin = serializer.save()
            admin.is_staff = True
            admin.is_superuser = True
            admin.set_password(serializer.validated_data['password'])  # Parolni xashlash
            admin.save()  # Qayta saqlash
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminDetailApi(APIView):
    @swagger_auto_schema(
        operation_description="Bitta admin ma’lumotini olish",
        responses={200: AdminSerializer(), 404: "Admin topilmadi"}
    )
    def get(self, request, id):
        admin = get_object_or_404(AdminModel, id=id)
        serializer = AdminSerializer(admin)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Admin ma’lumotlarini yangilash",
        request_body=AdminSerializer,
        responses={200: AdminSerializer(), 400: "Xato", 404: "Admin topilmadi"}
    )
    def put(self, request, id):
        admin = get_object_or_404(AdminModel, id=id)
        serializer = AdminSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Adminni o‘chirish",
        responses={204: "Muvaffaqiyatli o‘chirildi", 404: "Admin topilmadi"}
    )
    def delete(self, request, id):
        admin = get_object_or_404(AdminModel, id=id)
        admin.delete()
        return Response({'detail': 'Admin deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


from rest_framework.exceptions import NotFound


class UserListApi(APIView):
    """
    Foydalanuvchilar ro'yxatini yoki bitta foydalanuvchini olish uchun API
    """

    def get(self, request, id=None):
        try:
            if id:
                if not str(id).isdigit():
                    return Response(
                        {"error": "ID noto‘g‘ri formatda bo‘lishi kerak (raqam)."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                user = get_object_or_404(User, id=id)
                serializer = UserSerializer(user)
            else:
                users = User.objects.all()
                serializer = UserSerializer(users, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except NotFound:
            return Response(
                {"error": "Bunday foydalanuvchi topilmadi!"},
                status=status.HTTP_404_NOT_FOUND
            )



class DepartmentListCreateAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Barcha bo‘limlarni olish",
        responses={200: DepartmentSerializer(many=True)}
    )
    def get(self, request):
        departments = DepartmentModel.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Bo‘lim yaratish",
        request_body=DepartmentSerializer,
        responses={201: DepartmentSerializer()}
    )
    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepartmentDetailAPIView(APIView):
    """
    Bitta bo‘limni ko‘rish, yangilash va o‘chirish API si.
    """

    @swagger_auto_schema(
        operation_description="Bitta bo‘limni olish",
        responses={200: DepartmentSerializer()}
    )
    def get(self, request, pk):
        """ ID bo‘yicha bitta bo‘limni qaytaradi """
        try:
            department = DepartmentModel.objects.get(pk=pk)
            serializer = DepartmentSerializer(department)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DepartmentModel.DoesNotExist:
            return Response({"error": "Bo‘lim topilmadi"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Bo‘limni yangilash",
        request_body=DepartmentSerializer,
        responses={200: DepartmentSerializer()}
    )
    def put(self, request, pk):
        """ Bo‘lim ma’lumotlarini yangilaydi """
        try:
            department = DepartmentModel.objects.get(pk=pk)
        except DepartmentModel.DoesNotExist:
            return Response({"error": "Bo‘lim topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Bo‘limni o‘chirish",
        responses={204: "Deleted successfully"}
    )
    def delete(self, request, pk):
        """ ID bo‘yicha bo‘limni o‘chiradi """
        try:
            department = DepartmentModel.objects.get(pk=pk)
            department.delete()
            return Response({"message": "Bo‘lim o‘chirildi"}, status=status.HTTP_204_NO_CONTENT)
        except DepartmentModel.DoesNotExist:
            return Response({"error": "Bo‘lim topilmadi"}, status=status.HTTP_404_NOT_FOUND)



class GroupModelAPIView(APIView):
    """
    GroupModel ma'lumotlarini olish va yaratish uchun API.
    """

    @swagger_auto_schema(
        responses={200: GroupSerializer(many=True)},
        operation_description="Barcha GroupModel obyektlarini qaytaradi."
    )
    def get(self, request):
        groups = StudentGroupModel.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=GroupSerializer,
        responses={201: GroupSerializer()},
        operation_description="Yangi GroupModel obyektini yaratadi."
    )
    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupIDSView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'group_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
            },
            required=['group_ids'],
        ),
        responses={200: GroupSerializer(many=True)},
    )
    def post(self, request):
        group_ids = request.data.get("group_ids", [])
        groups = Group.objects.filter(id__in=group_ids)
        serializer = GroupSerializer(groups, many=True)
        return Response({"groups": serializer.data})

class StudentAPIView(APIView):

    @swagger_auto_schema(request_body=UserAndStudentSerializer)
    def post(self, request):
        user_data = request.data.get('user', {})
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save(is_student=True)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        student_data = request.data.get('student', {})
        student_serializer = StudentSerializer(data=student_data)
        if student_serializer.is_valid():
            student = student_serializer.save(user=user)
            return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)
        else:
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentDetailAPIView(APIView):

    def get(self, request, id):

        students = get_object_or_404(StudentModel, id=id)
        serializer = StudentSerializer(students)
        return Response(serializer.data)


        serializer_student = StudentSerializer(students, many=True)
        serializer_group = GroupSerializer(groups, many=True)
        serializer_course = CourseSerializer(courses, many=True)

        data = {
            "students": serializer_student.data,
            "groups": serializer_group.data,
            "courses": serializer_course.data
        }
        return Response(data=data)

    @swagger_auto_schema(request_body=StudentSerializer)
    def put(self, request, pk):
        try:
            student = StudentModel.objects.get(pk=pk)
        except StudentModel.DoesNotExist:
            return Response({'error': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSerializer(student, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={204: 'No Content'})
    def delete(self, request, pk):
        try:
            student = StudentModel.objects.get(pk=pk)
        except StudentModel.DoesNotExist:
            return Response({'error': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StatisticsView(APIView):
    """
    Ushbu API date1 va date2 oralig‘idagi statistikani chiqaradi.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date1 = request.GET.get('date1')
        date2 = request.GET.get('date2')

        if not date1 or not date2:
            return Response({"error": "date1 va date2 parametrlari kerak"}, status=400)

        date1 = parse_date(date1)
        date2 = parse_date(date2)

        if not date1 or not date2:
            return Response({"error": "Noto‘g‘ri sana formati"}, status=400)

        stats = {}
        for course in Course.objects.all():
            stats[course.name] = {
                "enrolled": StudentModel.objects.filter(course=course, status='enrolled', enrollment_date__range=[date1, date2]).count(),
                "active": StudentModel.objects.filter(course=course, status='active', enrollment_date__range=[date1, date2]).count(),
                "graduated": StudentModel.objects.filter(course=course, status='graduated', graduation_date__range=[date1, date2]).count()
            }

        return Response(stats)


class StudentsByRegistrationView(APIView):
    @swagger_auto_schema(request_body=DateRangeSerializer)
    def post(self, request):
        serializer = DateRangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_date = datetime.combine(serializer.validated_data.get('start_date'), datetime.min.time())
        end_date = datetime.combine(serializer.validated_data.get('end_date'), datetime.max.time())

        students = StudentModel.objects.filter(created__range=[start_date, end_date]).prefetch_related('course')

        # Faqat shu sanalar oralig‘idagi o‘quvchilarni hisobga olamiz
        is_studying = students.filter(is_line=True).count()
        is_compleated = students.filter(is_finished=True).count()

        # Kurslar bo‘yicha ro‘yxatdan o‘tganlar statistikasi
        course_counter = Counter()
        for student in students:
            course_counter[student.course.name] += 1

        response_data = {
            'course_registrations': [{'course': course, 'student_count': count} for course, count in course_counter.items()],
            'enrolled': is_studying,
            'graduated ': is_compleated,
        }

        return Response(response_data, status=status.HTTP_200_OK)

# class StudentStatusApiView(APIView):
#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter(
#                 'date1', openapi.IN_QUERY, description="Boshlang‘ich sana (YYYY-MM-DD)",
#                 type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=True
#             ),
#             openapi.Parameter(
#                 'date2', openapi.IN_QUERY, description="Tugash sanasi (YYYY-MM-DD)",
#                 type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=True
#             ),
#         ],
#         responses={200: StudentStatusSerializer(many=True)},
#         operation_description="Berilgan sana oralig‘ida har bir kurs bo‘yicha talabalar statistikasini qaytaradi."
#     )
#     def get(self, request):
#         date1 = request.query_params.get('date1')
#         date2 = request.query_params.get('date2')
#
#         if not date1 or not date2:
#             return Response({"error": "date1 va date2 parametrlari kerak"}, status=status.HTTP_400_BAD_REQUEST)
#
#         date1 = parse_date(date1)
#         date2 = parse_date(date2)
#
#         if not date1 or not date2:
#             return Response({"error": "Noto‘g‘ri sana formati (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)
#
#         if date1 > date2:
#             return Response({"error": "date1 date2 dan kichik yoki teng bo‘lishi kerak"}, status=status.HTTP_400_BAD_REQUEST)
#
#         #  To‘g‘ri ManyToMany bog‘lanishini ishlatish
#         groups = Group.objects.annotate(
#             enrolled_count=Count('students', filter=Q(students__enrollment_date__range=[date1, date2])),
#             active_students=Count('students', filter=Q(students__status='active')),
#             graduated_students=Count('students', filter=Q(students__status='graduated'))
#         )
#
#         serializer = StudentStatusSerializer(groups, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')  # CSRF tekshiruvini o‘chiradi
class StudentIDSView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'student_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
            },
            required=['student_ids'],
        ),
        responses={200: StudentSerializer(many=True)},
    )
    def post(self, request):
        student_ids = request.data.get("student_ids", [])
        students = StudentModel.objects.filter(id__in=student_ids)
        serializer = StudentSerializer(students, many=True)
        return Response({"students": serializer.data})




class StudentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class StudentListView(APIView):
    pagination_class = StudentPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Sahifa raqami", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Har bir sahifadagi elementlar soni", type=openapi.TYPE_INTEGER),
        ],
        responses={200: "List of students with id, full_name, and course"}
    )
    def get(self, request):
        students = StudentModel.objects.all().values('id', 'user__full_name', 'course')
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(students, request)
        return paginator.get_paginated_response(result_page)




class ParentListCreateAPIView(APIView):
    @swagger_auto_schema(request_body=ParentSerializer)
    def post(self, request):
        serializer = ParentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ParentDetailAPIView(APIView):
    @swagger_auto_schema(responses={200: ParentSerializer()})
    def get(self, request, pk):
        parent = get_object_or_404(ParentModel, pk=pk)
        serializer = ParentSerializer(parent)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ParentSerializer)
    def put(self, request, pk):
        parent = get_object_or_404(ParentModel, pk=pk)
        serializer = ParentSerializer(parent, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        parent = get_object_or_404(ParentModel, pk=pk)
        parent.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PaymentMonthDetailAPIView(APIView):
    @swagger_auto_schema(responses={200: PaymentMonthSerializer(many=True)})
    def get(self, request, id=None):
        """ Agar `id` berilsa bitta, aks holda barcha ma'lumotlarni qaytaradi """
        if id:
            month = get_object_or_404(PaymentMonth, id=id)
            serializer = PaymentMonthSerializer(month)
            return Response({"message": "Oylik to‘lov ma'lumoti", "data": serializer.data})
        else:
            months = PaymentMonth.objects.all()
            serializer = PaymentMonthSerializer(months, many=True)
            return Response({"message": "Barcha oylik to‘lovlar", "data": serializer.data})


    @swagger_auto_schema(request_body=PaymentMonthSerializer, responses={200: PaymentMonthSerializer()})
    def put(self, request, id):
        month = get_object_or_404(PaymentMonth, id=id)
        serializer = PaymentMonthSerializer(month, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Ma'lumot muvaffaqiyatli yangilandi!", "data": serializer.data})
        return Response({"error": "Yangilashda xatolik yuz berdi!", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: 'No Content'})
    def delete(self, request, id):
        month = get_object_or_404(PaymentMonth, id=id)
        month.delete()
        return Response({"message": "To‘lov oynasi muvaffaqiyatli o‘chirildi!"}, status=status.HTTP_204_NO_CONTENT)


class PaymentMonthAPIView(APIView):
    def handle_exception(self, exc):
        """ Xatolarni chiroyli formatda chiqarish """
        if isinstance(exc, Http404):
            return Response({"error": "Ma'lumot topilmadi!"}, status=status.HTTP_404_NOT_FOUND)
        elif isinstance(exc, ValidationError):
            return Response({"error": "Kiritilgan ma'lumot xato!", "details": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exc, IntegrityError):
            return Response({"error": "Bazaga ma'lumot qo‘shishda xatolik yuz berdi!"}, status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)  # Standart DRF xatolarini saqlab qolish

    @swagger_auto_schema(request_body=PaymentMonthSerializer)
    def post(self, request):
        serializer = PaymentMonthSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "To‘lov oynasi muvaffaqiyatli qo‘shildi!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": "Kiritilgan ma'lumotlar noto‘g‘ri!", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class PaymentTypeDetailAPIView(APIView):
    @swagger_auto_schema(responses={200: PaymentTypeSerializer(many=True)})
    def get(self, request, id=None):
        """ Agar 'id' berilsa bitta, aks holda barcha ma'lumotlarni qaytaradi """
        if id:
            type = get_object_or_404(PaymentType, id=id)
            serializer = PaymentTypeSerializer(type)
            return Response({"message": "To'lov turi", "data": serializer.data})
        else:
            types = PaymentType.objects.all()
            serializer = PaymentTypeSerializer(types, many=True)
            return Response({"message": "Barcha to'lov turlari", "data": serializer.data})

    @swagger_auto_schema(request_body=PaymentTypeSerializer, responses={200: PaymentTypeSerializer()})
    def put(self, request, id):
        type_obj = get_object_or_404(PaymentType, id=id)
        serializer = PaymentTypeSerializer(type_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: 'No Content'})
    def delete(self, request, id):
        type_obj = get_object_or_404(PaymentType, id=id)
        type_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentTypeAPIView(APIView):
    @swagger_auto_schema(request_body=PaymentTypeSerializer)
    def post(self, request):
        serializer = PaymentTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentDetailAPIView(APIView):
    @swagger_auto_schema(responses={200: PaymentTypeSerializer(many=True)})
    def get(self, request, id=None):
        """ Agar 'id' berilsa bitta, aks holda barcha ma'lumotlarni qaytaradi """
        if id:
            payment = get_object_or_404(Payment, id=id)
            serializer = PaymentSerializer(payment)
            return Response({"message": "To'lovni ko'rish", "data": serializer.data})
        else:
            payments = Payment.objects.all()
            serializer = PaymentSerializer(payments, many=True)
            return Response({"message": "Barcha to'lovlar", "data": serializer.data})

    @swagger_auto_schema(request_body=PaymentSerializer, responses={200: PaymentSerializer()})

    def put(self, request, id):
        payment = get_object_or_404(Payment, id=id)
        serializer = PaymentSerializer(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: 'No Content'})
    def delete(self, request, id):
        payment = get_object_or_404(Payment, id=id)
        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PaymentAPIView(APIView):
    @swagger_auto_schema(request_body=PaymentSerializer)
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TeacherAPIView(APIView):
    pagination_class = PageNumberPagination

    @swagger_auto_schema(request_body=UserAndTeacherSerializer)
    def post(self, request):
        user_data = request.data.get('user', {})
        teacher_data = request.data.get('teacher', {})

        if 'full_name' not in teacher_data:
            teacher_data['full_name'] = user_data.get('full_name')

        if not teacher_data.get('full_name'):
            return Response({'error': 'full_name is required'}, status=status.HTTP_400_BAD_REQUEST)

        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save(is_teacher=True)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        teacher_data['user'] = user.id

        teacher_serializer = TeacherSerializer(data=teacher_data)
        if teacher_serializer.is_valid():
            teacher = teacher_serializer.save(user=user)
            return Response(TeacherSerializer(teacher).data, status=status.HTTP_201_CREATED)
        else:
            return Response(teacher_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TeacherGroupsAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Authentifikatsiya talab qilinadi

    @swagger_auto_schema(
        operation_description="O‘qituvchining barcha guruhlarini olish",
        responses={
            200: TeacherGroupSerializer(many=True),  # Ko‘plab guruhlarni qaytaradi
            404: openapi.Response(description="Teacher not found"),
        },
    )
    def get(self, request, id):
        teacher = get_object_or_404(TeacherModel, id=id)  # O‘qituvchi obyektini olish
        groups = teacher.groups.all()  # O‘qituvchiga tegishli barcha guruhlar

        serializer = TeacherGroupSerializer(groups, many=True)  # TO‘G‘RI O‘ZGARTIRISH
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentGroupsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'group_id',
                openapi.IN_PATH,
                description="Talabaning guruh ID-si",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: GroupSerializer()},
        operation_description="Talaba o'ziga tegishli aniq bir guruhni ko'rishi mumkin."
    )
    def get(self, request, group_id):
        student = get_object_or_404(StudentModel, user=request.user)

        # Talaba faqat o‘zining guruhiga tegishli bo‘lsa, ko‘ra olishi kerak
        if student.group.id != group_id:
            return Response({'error': 'Siz bu guruhga tegishli emassiz!'}, status=status.HTTP_403_FORBIDDEN)

        serializer = GroupSerializer(student.group)  # To‘g‘ridan-to‘g‘ri chaqiramiz
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupStudentsAPIView(APIView):
    """
    Guruhga tegishli barcha studentlarni ko‘rish.
    Talabalar faqat o‘z guruhidagi talabalarni ko‘rishi mumkin.
    O‘qituvchi o‘z guruhiga tegishli barcha talabalarni ko‘ra oladi.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "group_id", openapi.IN_QUERY,
                description="Guruh ID sini kiriting",
                type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={200: StudentSerializer(many=True)},
        operation_description="Guruh bo‘yicha studentlarni ko‘rish."
    )
    def get(self, request):
        group_id = request.query_params.get("group_id")

        if not group_id:
            return Response({"error": "Guruh ID talab qilinadi"}, status=400)

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Bunday guruh topilmadi"}, status=404)

        user = request.user

        if hasattr(user, "teachermodel"):  # Agar foydalanuvchi o‘qituvchi bo‘lsa
            if group.teacher != user.teachermodel:
                return Response({"error": "Bu guruhga kirish huquqiga ega emassiz"}, status=403)
        elif hasattr(user, "studentmodel"):  # Agar foydalanuvchi talaba bo‘lsa
            if group not in user.studentmodel.groups.all():
                return Response({"error": "Bu guruhga kirish huquqiga ega emassiz"}, status=403)
        else:
            return Response({"error": "Foydalanuvchi turi noma’lum"}, status=403)

        students = group.students.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=200)


class GroupMonthlyDataAPIView(APIView, PageNumberPagination):
    """
    Guruh bo‘yicha oyma-oy ma’lumotlarni chiqarish.
    Har bir paginatsiyada 30 yoki 31 ta yozuv bo‘ladi.
    """
    permission_classes = [IsAuthenticated]
    page_size = 31  # Har bir sahifada maksimal 31 ta yozuv bo‘lishi kerak

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("group_id", openapi.IN_QUERY, description="Guruh ID sini kiriting", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter("month", openapi.IN_QUERY, description="Oy (YYYY-MM)", type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: AttendanceSerializer(many=True)},
        operation_description="Guruh bo‘yicha har oyda yozilgan ma’lumotlarni ko‘rish."
    )
    def get(self, request):
        group_id = request.query_params.get("group_id")
        month = request.query_params.get("month")

        if not group_id or not month:
            return Response({"error": "Guruh ID va oy parametrlari kerak"}, status=400)

        # Guruhni olish
        group = get_object_or_404(Group, id=group_id)

        user = request.user

        # Foydalanuvchi ruxsatini tekshirish
        if hasattr(user, "teachermodel"):  # Agar foydalanuvchi o‘qituvchi bo‘lsa
            if not group.teacher.filter(id=user.teachermodel.id).exists():  # ManyToManyField uchun
                return Response({"error": "Bu guruhga kirish huquqiga ega emassiz"}, status=403)
        elif hasattr(user, "studentmodel"):  # Agar foydalanuvchi talaba bo‘lsa
            if user.studentmodel.group != group:  # Agar ForeignKey bo‘lsa
                return Response({"error": "Bu guruhga kirish huquqiga ega emassiz"}, status=403)
        else:
            return Response({"error": "Foydalanuvchi turi noma’lum"}, status=403)

        # Sana formatini tekshirish
        start_date = parse_date(f"{month}-01")
        if not start_date:
            return Response({"error": "Noto‘g‘ri sana formati (YYYY-MM)"}, status=400)

        # Oyning oxirgi kunini hisoblash
        last_day = calendar.monthrange(start_date.year, start_date.month)[1]
        end_date = date(start_date.year, start_date.month, last_day)

        # Davomatni olish
        attendances = AttendanceModel.objects.filter(group=group, date__range=(start_date, end_date))
        result_page = self.paginate_queryset(attendances, request, view=self)
        serializer = AttendanceSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)

class StudentHomeworkAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: HomeworkSerializer(many=True)})
    def get(self, request):
        student = get_object_or_404(StudentModel, user=request.user)
        homeworks = Homework.objects.filter(group=student.group)  # ✅ ForeignKey bo‘lsa, `.all()` kerak emas
        serializer = HomeworkSerializer(homeworks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentGroupAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: GroupSerializer(many=True)})
    def get(self, request):
        student = StudentModel.objects.get(user=request.user)
        serializer = GroupSerializer(student.groups.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentAttendanceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER)
        ],
        responses={200: AttendanceSerializer(many=True)}
    )
    def get(self, request):
        student = get_object_or_404(StudentModel, user=request.user)

        # Talabaning davomatini olish
        attendance_qs = AttendanceModel.objects.filter(student=student).order_by('-date')

        # Paginatsiya
        paginator = Paginator(attendance_qs, 30)
        page = request.GET.get('page', 1)
        paginated_data = paginator.get_page(page)

        # Serializatsiya va natija
        serializer = AttendanceSerializer(paginated_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentGroupListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: StudentSerializer(many=True)})
    def get(self, request, group_id):
        student = get_object_or_404(StudentModel, user=request.user)

        if student.group.id != group_id:  # ✅ "filter" o‘rniga to‘g‘ridan-to‘g‘ri tekshirish
            return Response({'error': 'Siz bu guruhga tegishli emassiz!'}, status=status.HTTP_403_FORBIDDEN)

        serializer = StudentSerializer(student.group.student_groups.all(), many=True)  # "related_name" ishlatish
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeacherGroupAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: GroupSerializer(many=True)})
    def get(self, request):
        teacher = TeacherModel.objects.get(user=request.user)
        serializer = GroupSerializer(teacher.groups.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeacherGroupDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: GroupSerializer()})
    def get(self, request, group_id):
        # O'qituvchini topish yoki xatolik qaytarish
        teacher = get_object_or_404(TeacherModel, user=request.user)

        # Guruhni tekshirish
        group = get_object_or_404(teacher.groups, id=group_id)

        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TeacherGroupStudentsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: StudentSerializer(many=True)})
    def get(self, request, group_id):
        teacher = TeacherModel.objects.get(user=request.user)
        group = teacher.groups.filter(id=group_id).first()
        if not group:
            return Response({'error': 'Siz bu guruhga tegishli emassiz'}, status=status.HTTP_403_FORBIDDEN)
        serializer = StudentSerializer(group.students.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class TableTypeDeleteApi(APIView):
    @swagger_auto_schema(
        operation_description="Bitta table turi ma’lumotini olish",
        responses={200: TableTypeSerializer(), 404: "Topilmadi"}
    )
    def get(self, request, id):
        table_type = get_object_or_404(TableTypeModel, id=id)
        serializer = TableTypeSerializer(table_type)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Table turini yangilash",
        request_body=TableTypeSerializer,
        responses={200: TableTypeSerializer(), 400: "Xato", 404: "Topilmadi"}
    )
    def put(self, request, id):
        table_type = get_object_or_404(TableTypeModel, id=id)
        serializer = TableTypeSerializer(table_type, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Table turini o‘chirish",
        responses={204: "Muvaffaqiyatli o‘chirildi", 404: "Topilmadi"}
    )
    def delete(self, request, id):
        table_type = get_object_or_404(TableTypeModel, id=id)
        table_type.delete()
        return Response({'detail': 'Table type deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class TableListCreateApi(APIView):
    @swagger_auto_schema(
        operation_description="Barcha table ro‘yxatini olish",
        responses={200: TableSerializer(many=True)}
    )
    def get(self, request):
        tables = TableModel.objects.all()
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Yangi table yaratish",
        request_body=TableSerializer,
        responses={201: TableSerializer(), 400: "Xato"}
    )
    def post(self, request):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TableDetailApi(APIView):
    @swagger_auto_schema(
        operation_description="Bitta table ma’lumotini olish",
        responses={200: TableSerializer(), 404: "Topilmadi"}
    )
    def get(self, request, id):
        table = get_object_or_404(TableModel, id=id)
        serializer = TableSerializer(table)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Table ma’lumotlarini yangilash",
        request_body=TableSerializer,
        responses={200: TableSerializer(), 400: "Xato", 404: "Topilmadi"}
    )
    def put(self, request, id):
        table = get_object_or_404(TableModel, id=id)
        serializer = TableSerializer(table, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Table ma’lumotini o‘chirish",
        responses={204: "Muvaffaqiyatli o‘chirildi", 404: "Topilmadi"}
    )
    def delete(self, request, id):
        table = get_object_or_404(TableModel, id=id)
        table.delete()
        return Response({'detail': 'Table deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class AttendanceAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Yangi davomat qo‘shish uchun POST so‘rov.",
        request_body=AttendanceSerializer,
        responses={
            201: AttendanceSerializer,
            400: "Xato: Ma’lumotlar noto‘g‘ri kiritildi"
        }
    )
    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AttendanceGetPIView(APIView):
    @swagger_auto_schema(
        operation_description="Berilgan ID bo‘yicha davomat ma’lumotlarini olish.",
        responses={
            200: AttendanceSerializer,
            404: "Xato: Davomat topilmadi"
        }
    )
    def get(self, request, id):
        try:
            attendance = AttendanceModel.objects.get(id=id)
            serializer = AttendanceSerializer(attendance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AttendanceModel.DoesNotExist:
            return Response({"error": "Davomat topilmadi"}, status=status.HTTP_404_NOT_FOUND)

class AttendancePUTAIView(APIView):
    @swagger_auto_schema(
        operation_description="Berilgan ID bo‘yicha davomatni yangilash uchun PUT so‘rov.",
        request_body=AttendanceSerializer,
        responses={
            200: AttendanceSerializer,
            400: "Xato: Ma’lumotlar noto‘g‘ri kiritildi",
            404: "Xato: Davomat topilmadi"
        }
    )
    def put(self, request, id):
        try:
            attendance = AttendanceModel.objects.get(id=id)
            serializer = AttendanceSerializer(attendance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AttendanceModel.DoesNotExist:
            return Response({"error": "Davomat topilmadi"}, status=status.HTTP_404_NOT_FOUND)

class AttendanceDelatePIView(APIView):
    @swagger_auto_schema(
        operation_description="Berilgan ID bo‘yicha davomatni o‘chirish uchun DELETE so‘rov.",
        responses={
            204: "Muvaffaqiyatli o‘chirildi",
            404: "Xato: Davomat topilmadi"
        }
    )
    def delete(self, request, id):
        try:
            attendance = AttendanceModel.objects.get(id=id)
            attendance.delete()
            return Response({"message": "Davomat o‘chirildi"}, status=status.HTTP_204_NO_CONTENT)
        except AttendanceModel.DoesNotExist:
            return Response({"error": "Davomat topilmadi"}, status=status.HTTP_404_NOT_FOUND)


class AttendanceStatusAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Yangi davomat holatini qo‘shish",
        request_body=AttendanceStatusSerializer,
        responses={201: AttendanceStatusSerializer, 400: "Xato: Noto‘g‘ri ma’lumot"}
    )
    def post(self, request):
        serializer = AttendanceStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AttendanceStatusGetAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Barcha davomat holatlari ro‘yxatini olish yoki ID bo‘yicha bitta holatni olish",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="Status ID (ixtiyoriy)", type=openapi.TYPE_INTEGER),
        ],
        responses={200: AttendanceStatusSerializer(many=True), 404: "Topilmadi"}
    )
    def get(self, request):
        status_id = request.query_params.get('id', None)
        if status_id:
            try:
                status_obj = AttendanceModel.objects.get(id=status_id)
                serializer = AttendanceStatusSerializer(status_obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except AttendanceModel.DoesNotExist:
                return Response({"error": "Davomat holati topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        else:
            statuses = AttendanceModel.objects.all()
            serializer = AttendanceStatusSerializer(statuses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

class AttendanceStatusPutAPIView(APIView):
    @swagger_auto_schema(
        operation_description="ID bo‘yicha davomat holatini yangilash",
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="Status ID", type=openapi.TYPE_INTEGER, required=True),
        ],
        request_body=AttendanceStatusSerializer,
        responses={200: AttendanceStatusSerializer, 400: "Xato", 404: "Topilmadi"}
    )
    def put(self, request, pk=None):
        try:
            status_obj = AttendanceModel.objects.get(pk=pk)
            serializer = AttendanceStatusSerializer(status_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AttendanceModel.DoesNotExist:
            return Response({"error": "Davomat holati topilmadi"}, status=status.HTTP_404_NOT_FOUND)

class AttendanceStatusDeleteAPIView(APIView):
    @swagger_auto_schema(
        operation_description="ID bo‘yicha davomat holatini o‘chirish",
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="Status ID", type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={204: "O‘chirildi", 404: "Topilmadi"}
    )
    def delete(self, request, pk=None):
        try:
            status_obj = AttendanceModel.objects.get(pk=pk)
            status_obj.delete()
            return Response({"message": "Davomat holati o‘chirildi"}, status=status.HTTP_204_NO_CONTENT)
        except AttendanceModel.DoesNotExist:
            return Response({"error": "Davomat holati topilmadi"}, status=status.HTTP_404_NOT_FOUND)



class UserAPI(APIView):
    @swagger_auto_schema(
        operation_description="Yangi foydalanuvchi qo'shish",
        request_body=UserSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserListView(APIView):
    @swagger_auto_schema(
        operation_description="Foydalanuvchilar ro‘yxatini olish",
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class CreateSuperUserView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Superuser yaratish",
        request_body=UserSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request):
        data = request.data
        data["is_superuser"] = True
        data["is_staff"] = True
        data["is_admin"] = True
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(data["password"])
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CreateStudentView(APIView):
    permission_classes = [IsAuthenticated]  # Faqat autentifikatsiyadan o‘tgan foydalanuvchilar

    @swagger_auto_schema(
        operation_description="Yangi student yaratish",
        request_body=StudentSerializer,
        responses={201: StudentSerializer}
    )
    def post(self, request):
        if StudentModel.objects.filter(user=request.user).exists():
            return Response({"error": "Siz allaqachon student sifatida ro‘yxatdan o‘tib bo‘lgansiz!"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Userni avtomatik bog‘lash
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateTeacherView(APIView):
    @swagger_auto_schema(
        operation_description="Yangi o‘qituvchi yaratish",
        request_body=UserAndTeacherSerializer,
        responses={201: UserAndTeacherSerializer}
    )
    def post(self, request):
        serializer = UserAndTeacherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateParentView(APIView):
    @swagger_auto_schema(
        operation_description="Yangi ota-ona qo‘shish",
        request_body=ParentSerializer,
        responses={201: ParentSerializer}
    )
    def post(self, request):
        serializer = ParentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)