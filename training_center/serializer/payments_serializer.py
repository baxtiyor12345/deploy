from rest_framework import serializers

from training_center.models.payments_model import Payments


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = "__all__"