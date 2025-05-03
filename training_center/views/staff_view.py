from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from training_center.add_pagination import CustomPaginator
from training_center.models.teacher_model import Departments
from training_center.permissions import IsStaffOrReadOnly
from training_center.serializer import DepartamentSerializer
from django.db.models import Count
from training_center.models import User, Student, GroupStudent


class DepartamentApi(APIView):
    @swagger_auto_schema(request_body=DepartamentSerializer)
    def post(self, request):
        serializer = DepartamentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        departament = Departments.objects.all().order_by('-id')
        paginator = CustomPaginator()
        paginator.page_size = 2
        result_page = paginator.paginate_queryset(departament, request)
        serializer = DepartamentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class StatisticsAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Statistik ma'lumotlar: foydalanuvchilar, talabalar, o'qituvchilar va guruhlar statistikasi.")
    def get(self, request):
        # Foydalanuvchilar soni
        total_users = User.objects.count()

        # Faol foydalanuvchilar soni
        active_users = User.objects.filter(is_active=True).count()

        # O'qituvchilar soni
        teachers_count = User.objects.filter(is_teacher=True).count()

        # Talabalar soni
        students_count = User.objects.filter(is_student=True).count()

        # Har bir guruhdagi talabalar soni
        group_stats = GroupStudent.objects.annotate(student_count=Count('get_student')).values('title', 'student_count')

        # Javobni qaytarish
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'teachers_count': teachers_count,
            'students_count': students_count,
            'group_stats': list(group_stats)
        })