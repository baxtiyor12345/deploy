from rest_framework import serializers
from .user_serializer import UserSerializer
from ..models import *


class TeacherSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    departments = serializers.PrimaryKeyRelatedField(
        queryset=Departments.objects.all(), many=True, required=False
    )

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'departments', 'descriptions']


class TeacherUserSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_admin = serializers.BooleanField(read_only=True)
    is_teacher = serializers.BooleanField(read_only=True)
    is_student = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'phone_number', 'password', 'email', 'is_active', 'is_staff', 'is_admin', 'is_teacher', 'is_student')


class TeacherPostSerializer(serializers.Serializer):
    user = TeacherUserSerializer()
    teacher = TeacherSerializer()