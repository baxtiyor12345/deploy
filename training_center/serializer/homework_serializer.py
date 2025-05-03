from training_center.models.homework_model import Homework, HomeworkSubmission
from rest_framework import serializers

class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_teacher:
            raise serializers.ValidationError("Only teachers can create homework.")
        return attrs


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkSubmission
        fields = '__all__'
        read_only_fields = ['student', 'submitted_at']