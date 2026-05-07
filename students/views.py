from django.shortcuts import render, redirect
from .models import Student

def home(request):
    students = Student.objects.all()
    return render(request, 'home.html', {'students': students})

def add_student(request):
    if request.method == 'POST':
        name = request.POST['name']
        roll = request.POST['roll']
        email = request.POST['email']
        course = request.POST['course']
        dob = request.POST['dob']

        Student.objects.create(
            name=name,
            roll_number=roll,
            email=email,
            course=course,
            date_of_birth=dob
        )
        return redirect('home')

    return render(request, 'add_student.html')
