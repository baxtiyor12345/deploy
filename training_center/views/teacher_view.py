from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from ..permissions import IsStaffOrReadOnly,IsTeacher,IsAdminOrTeacherLimitedEdit
from ..add_pagination import CustomPaginator
from ..models.teacher_model import Teacher
from ..serializer import  UserSerializer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..serializer.teacher_serializer import TeacherPostSerializer, TeacherSerializer, TeacherUpdateSerializer

# TEACHER TOLIQ ISHLAYAPDI

class Teacher_Api(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    #teacher ishlayapdi get
    @swagger_auto_schema(
        responses={200: TeacherPostSerializer(many=True)}
    )
    def get(self,request):
        data = {"success": True}
        teachers = Teacher.objects.all().order_by('-id')
        paginator = CustomPaginator()
        paginator.page_size = 2
        result_page = paginator.paginate_queryset(teachers, request)
        serializer =  TeacherPostSerializer(result_page, many=True)
        data["teacher"] = serializer.data
        return Response(serializer.data, status=status.HTTP_200_OK)
# post ishlayapdi
    @swagger_auto_schema(
        request_body=TeacherPostSerializer
    )
    def post(self, request):
        data = request.data.copy()  # dict nusxasini olamiz

        # 'departments' ni string bo‘lsa, listga aylantirish
        departments = data.get('departments', '')
        if isinstance(departments, str):
            data['departments'] = list(map(int, departments.split(',')))

        # 'course' ni string bo‘lsa, listga aylantirish
        course = data.get('course', '')
        if isinstance(course, str):
            data['course'] = list(map(int, course.split(',')))

        serializer = TeacherPostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=TeacherPostSerializer,
        manual_parameters=[

            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                description="O'zgartiriladigan  o'qituvchi IDsi",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: "Muvaffaqiyatli o'zgartirildi",
            404: "O'qituvchi topilmadi",
            500: "Server xatosi"
        }
    )
    def put(self, request):
        data = request.data.copy()  # So'rovni o'zgartirish uchun nusxa

        # 'departments' ni string bo'lsa, listga aylantiramiz
        departments = data.get('departments', '')
        if isinstance(departments, str):
            data['departments'] = list(map(int, departments.split(',')))

        # 'course' ni string bo'lsa, listga aylantiramiz
        course = data.get('course', '')
        if isinstance(course, str):
            data['course'] = list(map(int, course.split(',')))

        # IDni olish
        teacher_id = request.query_params.get('id')
        if not teacher_id:
            return Response({'detail': "ID ko'rsatilmagan."}, status=status.HTTP_400_BAD_REQUEST)

        teacher = get_object_or_404(Teacher, pk=teacher_id)

        serializer = TeacherPostSerializer(teacher, data=data)
        if serializer.is_valid():
            teacher = serializer.save()
            return Response(TeacherSerializer(teacher).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




    # {
    #     "id": 3,
    #     "departments": [2, 3]   namuna patch
    # }
    # patch teacherni qisman malumotlarini o'zgartiradi
    #   muhum joyi (partial=True) techerni qisman malumoti kelyotgani bildiradi
    @swagger_auto_schema(
        request_body=TeacherUpdateSerializer,
        responses={
            200: "Muvaffaqiyatli qisman yangilandi",
            400: "Noto‘g‘ri ma’lumot",
            404: "O'qituvchi topilmadi",
            500: "Server xatosi"
        }
    )
    def patch(self, request):
        data = request.data.copy()

        # 'departments' ni string bo‘lsa listga aylantirish
        departments = data.get('departments', '')
        if isinstance(departments, str):
            data['departments'] = list(map(int, departments.split(',')))

        # 'course' ni string bo‘lsa listga aylantirish
        course = data.get('course', '')
        if isinstance(course, str):
            data['course'] = list(map(int, course.split(',')))

        # IDni olish va tekshirish
        teacher_id = data.get('id')
        if not teacher_id:
            return Response({'detail': "ID ko‘rsatilmagan."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            teacher_id = int(teacher_id)
        except ValueError:
            return Response({'detail': "ID noto‘g‘ri formatda."}, status=status.HTTP_400_BAD_REQUEST)

        teacher = get_object_or_404(Teacher, id=teacher_id)

        # Qisman yangilash
        serializer = TeacherUpdateSerializer(teacher, data=data, partial=True)
        if serializer.is_valid():
            teacher = serializer.save()
            return Response(TeacherSerializer(teacher).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # delete ishlayapdi
    # teacherni o'chirish bunda user ham birgalikda o'chadi
    # удалит учителя с пользователем
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_QUERY,
                description="O'chiriladigan o'qituvchi IDsi",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: "Muvaffaqiyatli o'chirildi",
            404: "O'qituvchi topilmadi",
            500: "Server xatosi"
        }
    )
    def delete(self, request):
        data = {"success": True}

        try:
            # ID ni so'rovdan olish
            teacher_id = request.GET.get('id')
            if not teacher_id:
                return Response(
                    data={"success": False, "xabar": "ID parametri talab qilinadi"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # O'qituvchini topish
            teacher = get_object_or_404(Teacher, id=teacher_id)
            user = teacher.user  # Bog'langan foydalanuvchi

            # Transaction ichida o'chirish
            with transaction.atomic():
                teacher.delete()  # Avval o'qituvchini o'chiramiz
                user.delete()  # Keyin foydalanuvchini o'chiramiz

            return Response(
                data={"success": True, "xabar": "O'qituvchi muvaffaqiyatli o'chirildi"},
                status=status.HTTP_204_NO_CONTENT
            )

        except Teacher.DoesNotExist:
            return Response(
                data={"success": False, "xabar": "O'qituvchi topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as xato:
            return Response(
                data={"success": False, "xabar": str(xato)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

