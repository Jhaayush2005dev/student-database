
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    email = models.EmailField()
    course = models.CharField(max_length=100)
    date_of_birth = models.DateField()

    def __str__(self):
        return self.name