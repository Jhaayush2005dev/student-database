from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import SignUpForm, StudentForm
from .models import Student

@login_required
def home(request):
    students = Student.objects.order_by('name')
    course_count = Student.objects.values('course').distinct().count()
    return render(request, 'home.html', {
        'students': students,
        'course_count': course_count,
    })

def signup(request):
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
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully.')
            return redirect('home')
    else:
        form = StudentForm()

    return render(request, 'add_student.html', {'form': form})
