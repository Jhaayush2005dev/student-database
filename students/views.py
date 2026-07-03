from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import SignUpForm, StudentForm
from .models import Student


def ensure_default_user():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

@login_required
def home(request):
    ensure_default_user()
    students = Student.objects.order_by('name')
    course_count = Student.objects.values('course').distinct().count()
    return render(request, 'home.html', {
        'students': students,
        'course_count': course_count,
    })

def signup(request):
    ensure_default_user()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully. Welcome!')
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

@login_required
def add_student(request):
    ensure_default_user()
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully.')
            return redirect('home')
    else:
        form = StudentForm()

    return render(request, 'add_student.html', {'form': form})
