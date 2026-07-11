from django.contrib import admin
from .models import Student, UserProfile, Subject, ExamMapping, MarksLedger

# Register your models here.
admin.site.register(Student)
admin.site.register(UserProfile)
admin.site.register(Subject)
admin.site.register(ExamMapping)
admin.site.register(MarksLedger)