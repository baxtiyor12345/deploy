from rest_framework import serializers
from ..models import Student, User, GroupStudent
from .user_serializer import *


class StudentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(
        queryset=GroupStudent.objects.all(), many=True, required=False
    )
    class Meta:
        model = Student
        fields = ['id', 'user', 'group']


class StudentUserSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_teacher = serializers.BooleanField(read_only=True)
    is_student = serializers.BooleanField(read_only=True)
    is_admin = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'phone_number', 'password', 'email', 'is_active', 'is_staff', 'is_admin', 'is_teacher', 'is_student',)


class StudentPostSerializer(serializers.Serializer):
    user = StudentUserSerializer()
    student = StudentSerializer()