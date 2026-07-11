from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student

ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('faculty', 'Faculty'),
    ('student', 'Student'),
]


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'email', 'course', 'phone_number', 'branch']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name',
                'required': True,
            }),
            'roll_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Roll Number',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
                'required': True,
            }),
            'course': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject',
                'required': True,
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
            }),
            'branch': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Branch',
            }),
        }
        labels = {
            'roll_number': 'Roll Number',
            'phone_number': 'Phone Number',
            'course': 'Subject',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Normalize inputs and allow the same email if the student enrolls in a different subject/course.
        if not email:
            return email

        email_norm = email.strip().lower()
        course = self.cleaned_data.get('course')
        course_norm = course.strip().lower() if course and isinstance(course, str) else None

        if course_norm:
            exists = Student.objects.filter(email__iexact=email_norm, course__iexact=course_norm).exists()
            if exists:
                raise forms.ValidationError('A student with this email already exists for this subject.')
        else:
            # If no course provided, fall back to global uniqueness check (case-insensitive)
            if Student.objects.filter(email__iexact=email_norm).exists():
                raise forms.ValidationError('A student with this email already exists.')
        return email


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Register as')
    faculty_course = forms.CharField(required=False, label='Faculty Subjects',
                                     widget=forms.TextInput(attrs={'placeholder': 'e.g. Math, Physics, Chemistry'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email
