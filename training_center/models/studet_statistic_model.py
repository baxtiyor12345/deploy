from django.db import models
from .studend_model import *

class StudentStatistic(models.Model):
    name=models.CharField(Student)
    start_date=models.DateTimeField()
    end_date=models.DateTimeField()

    def __str__(self):
        return self.name
