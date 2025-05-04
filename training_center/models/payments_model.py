from django.db import models

from . import Student
from .group_model import GroupStudent
from .user_model import *


class Payments(models.Model):
    student = models.ForeignKey(Student, on_delete=models.RESTRICT, related_name='payments')
    group = models.ForeignKey(GroupStudent, on_delete=models.RESTRICT, null=True, blank=True)
    amount = models.IntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online', 'Online')
    ])
    is_paid = models.BooleanField(default=True)
    note = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.phone_number} - {self.amount} so'm"