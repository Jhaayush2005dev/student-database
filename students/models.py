from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

# 1. YOUR EXISTING MODEL (For the Student Database Records)
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    email = models.EmailField()
    course = models.CharField(max_length=100)
    # phone number and branch added; date_of_birth removed per UI request
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    marks = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)
    current_gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

# 2. NEW ROLE MODEL (For Login Permissions)
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    # For faculty users: the specific course they belong to
    course = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        if self.role == 'faculty' and self.course:
            return f"{self.user.username} - {self.role} ({self.course})"
        return f"{self.user.username} - {self.role}"

class Subject(models.Model):
    course_code = models.CharField(max_length=20)
    name = models.CharField(max_length=120, unique=True)
    credits = models.PositiveSmallIntegerField(default=3)
    max_marks = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"{self.course_code} - {self.name}"

class ExamMapping(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name

class MarksLedger(models.Model):
    STATUS_DRAFT = 'D'
    STATUS_FINALIZED = 'F'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_FINALIZED, 'Finalized'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam = models.ForeignKey(ExamMapping, on_delete=models.CASCADE)
    obtained_marks = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'subject', 'exam'], name='unique_student_subject_exam')
        ]

    def __str__(self):
        return f"{self.student.name} | {self.subject.name} | {self.exam.name}"


def update_student_aggregate(student):
    finalized_grades = MarksLedger.objects.filter(student=student, status=MarksLedger.STATUS_FINALIZED)
    results = finalized_grades.aggregate(total=Sum('obtained_marks'), count=Count('id'))
    total = results['total'] or 0
    count = results['count'] or 0

    student.marks = total
    student.total_marks = total
    if count:
        average_marks = Decimal(total) / Decimal(count)
        student.current_gpa = (average_marks / Decimal(10)).quantize(Decimal('0.01'))
    else:
        student.current_gpa = Decimal('0.00')
    student.save(update_fields=['marks', 'total_marks', 'current_gpa'])


@receiver(post_save, sender=MarksLedger)
def update_aggregate_after_save(sender, instance, **kwargs):
    update_student_aggregate(instance.student)


@receiver(post_delete, sender=MarksLedger)
def update_aggregate_after_delete(sender, instance, **kwargs):
    update_student_aggregate(instance.student)


# 3. SIGNALS (To auto-create a profile when someone signs up)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()