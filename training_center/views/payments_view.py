from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from training_center.models.payments_model import Payments
from training_center.serializer.payments_serializer import PaymentsSerializer


class PaymentsApi(APIView):

    @swagger_auto_schema(responses={200: PaymentsSerializer(many=True)})
    def get(self, request):
        payments = Payments.objects.all()
        serializer = PaymentsSerializer(payments, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=PaymentsSerializer)
    def post(self, request):
        serializer = PaymentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        return Response(data=serializer.errors)


class PaymentsPutPatchApi(APIView):
    @swagger_auto_schema(request_body=PaymentsSerializer)
    def put(self, request, pk):
        payment = get_object_or_404(Payments, pk=pk)
        serializer = PaymentsSerializer(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=PaymentsSerializer)
    def patch(self, request, pk):
        payment = get_object_or_404(Payments, pk=pk)
        serializer = PaymentsSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)