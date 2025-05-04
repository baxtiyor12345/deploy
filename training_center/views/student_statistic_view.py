from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializer import StatisticSerializer
from ..models.studend_model import Student
from ..permissions import IsAdminOrTeacherLimitedEdit


class StudentsStatisticsView(APIView):
    permission_classes = [IsAdminOrTeacherLimitedEdit]
    @swagger_auto_schema(request_body=StatisticSerializer)
    def post(self, request):
        serializer = StatisticSerializer(data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            registered_students = Student.objects.filter(created_ed__range=(start_date, end_date))

            finished_students = Student.objects.filter(group__end_date__range=(start_date, end_date))

            current_students = Student.objects.exclude(id__in=finished_students)

            registered_data = []
            for student in registered_students:
                end_dates = student.group.values_list('end_date', flat=True)
                registered_data.append({
                    "id": student.id,
                    "username": student.fullname,
                    "created_ed": student.created_ed,
                    "finished_date": max(end_dates) if end_dates else None
                })

            graduated_data = []
            for student in finished_students:
                end_dates = student.group.values_list('end_date', flat=True)
                graduated_data.append({
                    "id": student.id,
                    "username": student.fullname,
                    "created_ed": student.created_ed,
                    "finished_date": max(end_dates) if end_dates else None
                })

            current_data = []
            for student in current_students:
                end_dates = student.group.values_list('end_date', flat=True)
                current_data.append({
                    "id": student.id,
                    "username": student.fullname,
                    "created_ed": student.created_ed,
                    "finished_date": max(end_dates) if end_dates else None
                })

            return Response({
                "registered_students_count": len(registered_data),
                "finished_students_count": len(graduated_data),
                "current_students_count": len(current_data),
                "new_registered_students": registered_data,
                "finished_students": graduated_data,
                "current_students": current_data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
