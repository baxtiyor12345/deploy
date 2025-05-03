from drf_yasg.utils import swagger_serializer_method, swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from training_center.models.homework_model import Homework
from training_center.serializer.homework_serializer import HomeworkSerializer, HomeworkSubmissionSerializer
from ..permissions import IsAdminOrTeacherLimitedEdit
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import permissions



class HomeworkListCreateApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=HomeworkSerializer)
    def post(self, request):
        # Faqat Teacher foydalanuvchilar yaratishi kerak
        if not request.user.is_teacher:
            return Response({'detail': 'You do not have permission to create homework.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = HomeworkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if request.user.is_staff: #admin homework larni ko'rishi uchun
            homeworks = Homework.objects.all()
        else:
            homeworks = Homework.objects.filter(created_by=request.user) #teacher o'zi yaratgan homeworklarni ko'ra oladi
        serializer = HomeworkSerializer(homeworks, many=True)
        return Response(serializer.data)

class HomeworkSubmissionCreateApi(APIView): # Studentlar homework yuklashi uchun
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(request_body=HomeworkSubmissionSerializer)
    def post(self, request, homework_id):
        try:
            homework = Homework.objects.get(id=homework_id)
        except Homework.DoesNotExist:
            return Response({'detail': 'Homework not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = HomeworkSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user, homework=homework)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
