from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'email', 'course', 'date_of_birth']
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
                'placeholder': 'Course',
                'required': True,
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True,
            }),
        }
        labels = {
            'roll_number': 'Roll Number',
            'date_of_birth': 'Date of Birth',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Student.objects.filter(email=email).exists():
            raise forms.ValidationError('A student with this email already exists.')
        return email


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email
