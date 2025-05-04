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



class StudentPostSerializer(serializers.ModelSerializer):
    user = StudentUserSerializer()
    # id = serializers.IntegerField(read_only=True)
    # group = serializers.ListField(
    #     child=serializers.IntegerField(),
    #     required=False
    # )
    # is_line = serializers.BooleanField(required=False)
    # descriptions = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'group', 'is_line', 'descriptions']

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user_data["is_active"] = True
        user_data["is_student"] = True
        groups = validated_data.pop("group", [])

        user = User.objects.create_user(**user_data)
        student = Student.objects.create(user=user, **validated_data)

        # groups allaqachon obyektlar QuerySeti!
        student.group.set(groups)

        return student

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        groups = validated_data.pop("group", None)

        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if groups is not None:
            instance.group.set(groups)

        instance.save()
        return instance

class StudentUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    user = StudentUserSerializer(required=False)

    class Meta:
        model = Student
        fields = ['id', 'user', 'group', 'is_line', 'descriptions']
        extra_kwargs = {
            "id": {"required": True},
            "group": {"required": False},
            "is_line": {"required": False},
            "descriptions": {"required": False},
        }

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        groups = validated_data.pop("group", None)

        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if groups is not None:
            instance.group.set(groups)

        instance.save()
        return instance
