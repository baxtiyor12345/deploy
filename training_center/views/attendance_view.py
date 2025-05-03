from rest_framework import viewsets
from training_center.models.teacher_model import Teacher
from ..models.attendance_model import Attendance, StudentAttendance
from ..serializer.attendance_serializer import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from ..models import Teacher
from training_center.models.attendance_model import Attendance, StudentAttendance
from training_center.serializer.attendance_serializer import *


class AttendanceApi(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Foydalanuvchiga qarab attendance ro'yxatini qaytaradi",
        responses={200: AttendanceSerializer(many=True)}
    )
    def get(self, request):
        user = request.user

        if user.is_staff:
            attendances = Attendance.objects.all().order_by('-date')
        else:
            teacher = Teacher.objects.filter(user=user).first()
            if teacher:
                attendances = Attendance.objects.filter(group__teacher=teacher).order_by('-date')
            else:
                attendances = Attendance.objects.filter(group__teacher__user=user).order_by('-date')

        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=AttendanceSerializer,
        operation_description="Yangi attendance yozuvi yaratadi va unga bog'langan talabalar uchun avtomatik StudentAttendance yozadi.",
        responses={201: AttendanceSerializer}
    )
    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attendance = serializer.save()
        students = attendance.group.get_student.all()

        for student in students:
            StudentAttendance.objects.create(
                attendance=attendance,
                student=student,
                is_present=False
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AttendancePatchDeleteApi(APIView):

    @swagger_auto_schema(
        request_body=AttendanceSerializer,
        operation_description="Attendance yozuvini qisman yangilash (faqat kerakli maydonlar).",
        responses={200: AttendanceSerializer, 404: 'Not Found'}
    )
    def patch(self, request, pk):
        attendance = get_object_or_404(Attendance, pk=pk)
        serializer = AttendanceSerializer(attendance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Attendance yozuvini o'chirish",
        responses={204: 'Deleted', 404: 'Not Found'}
    )
    def delete(self, request, pk):
        attendance = get_object_or_404(Attendance, pk=pk)
        attendance.delete()
        return Response({"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT)


class StudentAttendanceApi(APIView):
    permission_classes = [IsAuthenticated]  # Barcha foydalanuvchilar uchun tekshirish

    @swagger_auto_schema(
        operation_description="StudentAttendance ro'yxatini ko'rish",
        responses={200: StudentAttendanceSerializer(many=True)}
    )
    def get(self, request):
        user = request.user

        if user.is_staff:
            queryset = StudentAttendance.objects.all()
        else:
            queryset = StudentAttendance.objects.filter(
                attendance__group__teacher__user=user
            )

        serializer = StudentAttendanceSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=StudentAttendanceSerializer,
        operation_description="Yangi StudentAttendance yozuvi yaratish (faqat admin)",
        responses={201: StudentAttendanceSerializer}
    )
    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Faqat admin foydalanuvchi yaratishi mumkin."}, status=status.HTTP_403_FORBIDDEN)

        serializer = StudentAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class StudentAttendancePutPatchDeleteApi(APIView):

    @swagger_auto_schema(
        request_body=StudentAttendanceSerializer,
        operation_description="StudentAttendance yozuvini yangilash (to‘liq PUT)",

    )
    def put(self, request, pk):
        instance = get_object_or_404(StudentAttendance, pk=pk)
        serializer = StudentAttendanceSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=StudentAttendanceSerializer,
        operation_description="StudentAttendance yozuvini qisman yangilash (PATCH)",

    )
    def patch(self, request, pk):
        instance = get_object_or_404(StudentAttendance, pk=pk)
        serializer = StudentAttendanceSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="StudentAttendance yozuvini o'chirish",
        responses={204: 'Deleted'}
    )
    def delete(self, request, pk):
        instance = get_object_or_404(StudentAttendance, pk=pk)
        instance.delete()
        return Response({"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT)