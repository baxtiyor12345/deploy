from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from ..permissions import *
from ..models import Student
from ..serializer.student_serializer import *
from ..add_pagination import CustomPaginator


#  HAMMASI ISHLAYAPDI

class StudentApi(APIView):
    permission_classes = (IsAuthenticated, IsStaffUser)

    # Studentlarni olish (GET)
    @swagger_auto_schema(
        responses={200: StudentPostSerializer(many=True)},
        description="Studentlar ro'yxatini olish"
    )
    def get(self, request):
        students = Student.objects.all().order_by('-id')
        paginator = CustomPaginator()
        paginator.page_size = 2
        result_page = paginator.paginate_queryset(students, request)
        serializer = StudentPostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # Yangi student yaratish (POST)
    @swagger_auto_schema(
        request_body=StudentPostSerializer,
        description="Yangi student yaratish"
    )
    def post(self, request):
        data = request.data.copy()  # dict nusxasini olamiz
        group = data.get('group', '')
        if isinstance(group, str):
            data['group'] = list(map(int, group.split(',')))
        serializer = StudentPostSerializer(data=data)
        if serializer.is_valid():
            student = serializer.save()
            return Response(data=StudentPostSerializer(student).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Studentni yangilash (PUT)
    @swagger_auto_schema(
        request_body=StudentPostSerializer,
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                description="O'zgartiriladigan student IDsi",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: "Muvaffaqiyatli yangilandi",
            404: "Student topilmadi",
            500: "Server xatosi"
        },
        description="Studentni yangilash"
    )
    def put(self, request):
        data = request.data.copy()  # dict nusxasini olamiz
        group = data.get('group', '')
        if isinstance(group, str):
            data['group'] = list(map(int, group.split(',')))

        student_id = request.query_params.get('id')
        if not student_id:
            return Response({'detail': "ID ko'rsatilmagan."}, status=status.HTTP_400_BAD_REQUEST)

        student = get_object_or_404(Student, pk=student_id)
        serializer = StudentPostSerializer(student, data=data)  # <-- to'g'riladik: data yuboriladi

        if serializer.is_valid():
            student = serializer.save()
            return Response(StudentPostSerializer(student).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Studentni qisman yangilash (PATCH)
    @swagger_auto_schema(
        request_body=StudentUpdateSerializer,
        responses={
            200: "Muvaffaqiyatli qisman yangilandi",
            400: "Noto‘g‘ri ma’lumot",
            404: "Student topilmadi",
            500: "Server xatosi"
        },
        description="Studentni qisman yangilash"
    )
    def patch(self, request):
        data = request.data.copy()  # dict nusxasini olamiz
        group = data.get('group', '')
        if isinstance(group, str):
            data['group'] = list(map(int, group.split(',')))

        student_id = data.get('id')
        if not student_id:
            return Response({'detail': "ID ko‘rsatilmagan."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student_id = int(student_id)
        except ValueError:
            return Response({'detail': "ID noto‘g‘ri formatda."}, status=status.HTTP_400_BAD_REQUEST)

        student = get_object_or_404(Student, id=student_id)
        serializer = StudentUpdateSerializer(student, data=data, partial=True)  # <-- data ni yuborayapmiz

        if serializer.is_valid():
            student = serializer.save()
            return Response(StudentPostSerializer(student).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Studentni o'chirish (DELETE)
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                description="O'chiriladigan student IDsi",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: "Muvaffaqiyatli o'chirildi",
            404: "Student topilmadi",
            500: "Server xatosi"
        },
        description="Studentni o'chirish"
    )
    def delete(self, request):
        data = {"success": True}

        try:
            # ID ni so'rovdan olish
            student_id = request.GET.get('id')
            if not student_id:
                return Response(
                    data={"success": False, "xabar": "ID parametri talab qilinadi"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Studentni topish
            student = get_object_or_404(Student, id=student_id)
            user = student.user  # Bog'langan foydalanuvchi

            # Transaction ichida o'chirish
            with transaction.atomic():
                student.delete()  # Avval studentni o'chiramiz
                user.delete()  # Keyin foydalanuvchini o'chiramiz

            return Response(
                data={"success": True, "xabar": "Student muvaffaqiyatli o'chirildi"},
                status=status.HTTP_204_NO_CONTENT
            )

        except Student.DoesNotExist:
            return Response(
                data={"success": False, "xabar": "Student topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                data={"success": False, "xabar": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
