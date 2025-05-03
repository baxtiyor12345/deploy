from django.db import models
from .studend_model import Student
from .teacher_model import Teacher


class Homework(models.Model): # Teacher Homework beradi
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='homeworks/', blank=True, null=True)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='homeworks')

    def __str__(self):
        return self.title


class HomeworkSubmission(models.Model): # Student topshirishi uchun
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='homework_submissions')
    file = models.FileField(upload_to='homework_submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.homework.title}"