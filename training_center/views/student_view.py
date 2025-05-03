from datetime import datetime
from django.contrib.auth.hashers import make_password
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from ..add_pagination import CustomPaginator
from ..models import Student, User, GroupStudent
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from ..permissions import IsStaffOrReadOnly
from ..serializer import StudentSerializer, StudentUserSerializer, StudentPostSerializer


class StudentApi(APIView):
    permission_classes = [IsStaffOrReadOnly]  # staff check

    @swagger_auto_schema(request_body=StudentPostSerializer)
    def post(self, request):
        data = {"success": True}
        user_data = request.data['user']
        student_data = request.data['student']

        user_serializer = StudentUserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)

        validated_user = user_serializer.validated_data
        validated_user['password'] = make_password(validated_user['password'])
        validated_user['is_student'] = True
        validated_user['is_active'] = True

        user = User.objects.create(**validated_user)

        student_serializer = StudentSerializer(data=student_data)
        student_serializer.is_valid(raise_exception=True)

        student = student_serializer.save(user=user)

        if 'departments' in student_data:
            student.departments.set(student_data['departments'])
        if 'course' in student_data:
            student.course.set(student_data['course'])

        data['user'] = StudentUserSerializer(user).data
        data['student'] = StudentSerializer(student).data
        return Response(data)
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Qaysi sahifa", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Har sahifadagi elementlar soni",
                              type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        students = Student.objects.all().order_by('-id')
        paginator = CustomPaginator()

        # Query paramdan page_size olish
        page_size = request.query_params.get('page_size')
        if page_size and page_size.isdigit():
            paginator.page_size = int(page_size)
        else:
            paginator.page_size = 2  # default

        result_page = paginator.paginate_queryset(students, request)
        serializer = StudentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class StudentPutPatchApi(APIView):
    permission_classes = [IsStaffOrReadOnly]  # Har doim auth + staff check

    @swagger_auto_schema(request_body=StudentPostSerializer)
    def put(self, request, pk):
        student = get_object_or_404(Student, pk=pk)

        # Foydalanuvchini yangilash
        user_data = request.data.get('user', {})
        user_serializer = StudentUserSerializer(student.user, data=user_data)
        if user_serializer.is_valid():
            # Parolni xash qilish
            if 'password' in user_serializer.validated_data:
                user_serializer.validated_data['password'] = make_password(user_serializer.validated_data['password'])
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Talabani yangilash
        student_data = request.data.get('student', {})
        student_serializer = StudentSerializer(student, data=student_data)
        if student_serializer.is_valid():
            student = student_serializer.save()

            # ManyToMany maydonlarni yangilash
            group_ids = student_data.get('group', [])
            student.group.set(group_ids)

            return Response(student_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=StudentPostSerializer)
    def patch(self, request, pk):
        student = get_object_or_404(Student, pk=pk)

        # Foydalanuvchini qisman yangilash
        user_data = request.data.get('user', {})
        if user_data:
            user_serializer = StudentUserSerializer(student.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                if 'password' in user_serializer.validated_data:
                    user_serializer.validated_data['password'] = make_password(
                        user_serializer.validated_data['password'])
                user_serializer.save()
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Talabani qisman yangilash
        student_data = request.data.get('student', {})
        student_serializer = StudentSerializer(student, data=student_data, partial=True)
        if student_serializer.is_valid():
            student = student_serializer.save()

            # ManyToMany maydonlarini yangilash
            group_ids = student_data.get('group', [])
            if group_ids:
                student.group.set(group_ids)

            return Response(student_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        student.user.delete()  # Agar user ham o‘chirilishi kerak bo‘lsa
        student.delete()
        return Response({"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT)


class StudentStatusByDateAPIView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'start_date', openapi.IN_QUERY, description="Boshlanish sanasi (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                'end_date', openapi.IN_QUERY, description="Tugash sanasi (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=True
            )
        ]
    )
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({'error': 'start_date va end_date kiritilishi shart!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({'error': 'Sana formati noto‘g‘ri. To‘g‘ri format: YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        finished_groups = GroupStudent.objects.filter(finish_date__range=(start_date, end_date))
        finished_students = Student.objects.filter(group__in=finished_groups).distinct()

        active_groups = GroupStudent.objects.filter(finish_date__isnull=True)
        active_students = Student.objects.filter(group__in=active_groups).distinct()

        return Response({
            'finished_students_count': finished_students.count(),
            'finished_students': [
                {
                    'id': s.id,
                    'phone_number': s.user.phone_number,
                    'groups': [g.title for g in s.group.all()]
                } for s in finished_students
            ],
            'active_students_count': active_students.count(),
            'active_students': [
                {
                    'id': s.id,
                    'phone_number': s.user.phone_number,
                    'groups': [g.title for g in s.group.all()]
                } for s in active_students
            ]
        })