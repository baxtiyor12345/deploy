from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register([Table,TableType,Teacher,Student,StudentAttendance,
                     GroupStudent,Payments,Homework,HomeworkSubmission,Room,Departments,Course])
