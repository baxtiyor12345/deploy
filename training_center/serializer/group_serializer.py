from rest_framework import serializers
from ..models import *


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupStudent
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = "__all__"

class TableTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableType
        fields = "__all__"

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"

class DepartamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = '__all__'