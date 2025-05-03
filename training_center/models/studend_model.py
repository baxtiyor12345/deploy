from .group_model import *
from .teacher_model import *
from .user_model import *

class Student(BaseModel):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    group = models.ManyToManyField(GroupStudent,related_name='get_student')
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.user.phone_number