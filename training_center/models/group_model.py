from .teacher_model import *
from .user_model import *
from django.db import models


class Room(BaseModel):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title


class TableType(BaseModel):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title


class Table(BaseModel):
    start_time = models.TimeField(null=True, blank=True)
    finish_time = models.TimeField(null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.RESTRICT)
    type = models.ForeignKey(TableType, on_delete=models.RESTRICT)
    descriptions = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.start_time.__str__() + " " + self.finish_time.__str__()


class GroupStudent(BaseModel):
    title = models.CharField(max_length=40, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ManyToManyField(Teacher, related_name='teacher_get')
    table = models.ForeignKey(Table, on_delete=models.RESTRICT,  null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title