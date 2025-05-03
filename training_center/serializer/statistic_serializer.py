from rest_framework import serializers

from ..models import StudentStatistic

class StatisticSerializer(serializers.ModelSerializer):

    class Meta:
        model=StudentStatistic
        fields="__all__"