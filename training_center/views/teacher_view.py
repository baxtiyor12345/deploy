from ftplib import error_temp
from django.contrib.auth.hashers import make_password
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from training_center.models import Teacher, GroupStudent
from training_center.serializer.teacher_serializer import TeacherSerializer
from ..add_pagination import CustomPaginator
from django.shortcuts import get_object_or_404
from ..models.payments_model import Payments
from ..permissions import IsTeacher
from training_center.serializer.payments_serializer import PaymentsSerializer
from training_center.serializer.teacher_serializer import TeacherSerializer, TeacherPostSerializer, TeacherUserSerializer
from ..models import User
from ..serializer.detail_teacher import GroupStudentDetailSerializer


class TeacherApi(APIView):
    @swagger_auto_schema(request_body=TeacherPostSerializer)
    def post(self, request):
        data = {"success": True}
        user_data = request.data['user']
        teacher_data = request.data['teacher']

        user_serializer = TeacherUserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)

        validated_user = user_serializer.validated_data
        validated_user['password'] = make_password(validated_user['password'])
        validated_user['is_teacher'] = True
        validated_user['is_active'] = True

        user = User.objects.create(**validated_user)

        teacher_serializer = TeacherSerializer(data=teacher_data)
        teacher_serializer.is_valid(raise_exception=True)

        teacher = teacher_serializer.save(user=user)

        if 'departments' in teacher_data:
            teacher.departments.set(teacher_data['departments'])
        if 'course' in teacher_data:
            teacher.course.set(teacher_data['course'])

        data['user'] = TeacherUserSerializer(user).data
        data['teacher'] = TeacherSerializer(teacher).data
        return Response(data)

    def get(self, request):
        teachers = Teacher.objects.all().order_by('-id')
        paginator = CustomPaginator()
        paginator.page_size = 2
        result_page = paginator.paginate_queryset(teachers, request)
        serializer = TeacherSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class TeacherPutPatchApi(APIView):
    @swagger_auto_schema(request_body=TeacherPostSerializer)
    def put(self, request, pk):
        teacher = get_object_or_404(Teacher, pk=pk)

        # 1. Userni to‘liq yangilaymiz
        user_data = request.data.get("user")
        if not user_data:
            return Response({"user": "required"}, status=status.HTTP_400_BAD_REQUEST)

        user_serializer = TeacherUserSerializer(teacher.user, data=user_data)
        user_serializer.is_valid(raise_exception=True)

        if 'password' in user_serializer.validated_data:
            user_serializer.validated_data['password'] = make_password(user_serializer.validated_data['password'])

        user_serializer.save()

        # 2. Teacher obyektini to‘liq yangilaymiz
        teacher_data = request.data.get("teacher")
        if not teacher_data:
            return Response({"teacher": "required"}, status=status.HTTP_400_BAD_REQUEST)

        teacher_serializer = TeacherSerializer(teacher, data=teacher_data)
        teacher_serializer.is_valid(raise_exception=True)
        teacher = teacher_serializer.save()

        # ManyToMany
        departments = teacher_data.get("departments")
        if departments is not None:
            teacher.departments.set(departments)

        return Response(TeacherSerializer(teacher).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=TeacherPostSerializer)
    def patch(self, request, pk):
        teacher = get_object_or_404(Teacher, pk=pk)

        # 1. User qismi
        user_data = request.data.get("user", {})
        if user_data:
            user_serializer = TeacherUserSerializer(teacher.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                if 'password' in user_serializer.validated_data:
                    user_serializer.validated_data['password'] = make_password(
                        user_serializer.validated_data['password'])
                user_serializer.save()
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 2. Teacher qismi
        teacher_data = request.data.get("teacher", {})
        teacher_serializer = TeacherSerializer(teacher, data=teacher_data, partial=True)
        if teacher_serializer.is_valid():
            teacher = teacher_serializer.save()

            # ManyToMany maydonlarni alohida set qilish (masalan: departments)
            department_ids = teacher_data.get("departments", None)
            if department_ids is not None:
                teacher.departments.set(department_ids)

            return Response(TeacherSerializer(teacher).data, status=status.HTTP_200_OK)
        else:
            return Response(teacher_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherGroupInfoAPIView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        teacher = Teacher.objects.get(user=request.user)
        groups = GroupStudent.objects.filter(teacher=teacher).distinct()
        serializer = GroupStudentDetailSerializer(groups, many=True)
        return Response(serializer.data)