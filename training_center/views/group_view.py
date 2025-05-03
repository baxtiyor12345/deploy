from django.contrib.admin.templatetags.admin_list import pagination
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from training_center.add_pagination import CustomPaginator
from training_center.models import GroupStudent, Course
from training_center.serializer.group_serializer import GroupSerializer
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsAdminOrTeacherLimitedEdit, IsStaffOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from training_center.serializer.group_serializer import CourseSerializer


class GroupApi(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]  # Har doim auth + staff check

    @swagger_auto_schema(request_body=GroupSerializer)
    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        group_title = GroupStudent.objects.all().order_by('-id')
        paginator = CustomPaginator()
        paginator.page_size = 2
        result_page = paginator.paginate_queryset(group_title, request)
        serializer = GroupSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class GroupStudentDetailUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrTeacherLimitedEdit, IsStaffOrReadOnly]

    @swagger_auto_schema(request_body=GroupSerializer)
    def patch(self, request, pk):
        group_title = get_object_or_404(GroupStudent, pk=pk)
        self.check_object_permissions(request, group_title)
        serializer = GroupSerializer(group_title, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseApi(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly ]  # Har doim auth + staff check

    @swagger_auto_schema(request_body=CourseSerializer)
    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        course_title = Course.objects.all().order_by('-id')
        paginator = CustomPaginator()
        result_page = paginator.paginate_queryset(course_title, request)
        serializer = CourseSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CoursePutPatchApi(APIView):
    permission_classes = [IsAuthenticated]  # Har doim auth + staff check

    @swagger_auto_schema(request_body=CourseSerializer)
    def put(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=CourseSerializer)
    def patch(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)