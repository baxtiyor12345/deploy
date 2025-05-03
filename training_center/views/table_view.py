from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from training_center.add_pagination import CustomPaginator
from training_center.models import Table
from training_center.serializer import TableSerializer, RoomSerializer, TableTypeSerializer
from training_center.models.group_model import *


class RoomApi(APIView):
    @swagger_auto_schema(request_body=RoomSerializer)
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        room = Room.objects.all().order_by('-id')
        paginator = CustomPaginator()
        paginator.page_size = 2
        result_page = paginator.paginate_queryset(room, request)
        serializer = RoomSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class TableApi(APIView):
    @swagger_auto_schema(request_body=TableSerializer)
    def post(self, request):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        table_title = Table.objects.all().order_by('-id')
        paginator = CustomPaginator()
        paginator.page_size = 2
        result_page = paginator.paginate_queryset(table_title, request)
        serializer = TableSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class TableTypeApi(APIView):
    @swagger_auto_schema(request_body=TableTypeSerializer)
    def post(self, request):
        tabletype = TableType.objects.all().order_by('-id')
        serializer = TableTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        tabletype = TableType.objects.all().order_by('-id')
        paginator = CustomPaginator()
        paginator.page_size = 2
        result_page = paginator.paginate_queryset(tabletype, request)
        serializer = TableSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


