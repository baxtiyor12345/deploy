from rest_framework import serializers
from training_center.models import GroupStudent, Student  # Tashqi modellardan foydalanish uchun
from training_center.models.attendance_model import StudentAttendance, Attendance


# StudentAttendance modelining oddiy serializeri
class StudentAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)  # agar student modeli `full_name` bor bo'lsa

    class Meta:
        model = StudentAttendance
        fields = ['id', 'attendance', 'student', 'student_name', 'is_present']
        read_only_fields = ['attendance', 'student_name']


class AttendanceSerializer(serializers.ModelSerializer):
    student_attendances = StudentAttendanceSerializer(many=True, read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'group', 'date', 'lesson_name', 'descriptions', 'student_attendances']