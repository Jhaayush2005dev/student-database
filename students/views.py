from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import SignUpForm, StudentForm
from .models import Student, UserProfile, Subject, ExamMapping, MarksLedger

def ensure_default_user():
    admin_qs = User.objects.filter(username='admin')
    if not admin_qs.exists():
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        # ensure admin profile role is set
        admin.userprofile.role = 'admin'
        admin.userprofile.save()
    else:
        admin = admin_qs.first()
        # if profile exists but role not admin, fix it
        try:
            if admin.userprofile.role != 'admin':
                admin.userprofile.role = 'admin'
                admin.userprofile.save()
        except UserProfile.DoesNotExist:
            # create profile and set role
            UserProfile.objects.create(user=admin, role='admin')


def get_user_role(user):
    try:
        return user.userprofile.role
    except UserProfile.DoesNotExist:
        return 'student'


def get_user_subjects(user):
    try:
        raw = user.userprofile.course or ''
        return [subject.strip() for subject in raw.split(',') if subject.strip()]
    except UserProfile.DoesNotExist:
        return []


def get_selected_subject(request, user):
    subjects = get_user_subjects(user)
    selected = request.GET.get('subject', '').strip()
    if selected and selected in subjects:
        return selected
    return subjects[0] if subjects else None


def get_faculty_subject_objects(user):
    names = get_user_subjects(user)
    subjects = []
    for name in names:
        subject, _ = Subject.objects.get_or_create(
            name=name,
            defaults={
                'course_code': name[:8].upper(),
                'credits': 3,
                'max_marks': 100,
            }
        )
        subjects.append(subject)
    return subjects


def role_login(request, role):
    ensure_default_user()
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if get_user_role(user) != role:
                messages.error(request, f'Please use the {role} login page for this account.')
                return render(request, f'{role}_login.html', {'form': form, 'role': role})

            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, f'{role}_login.html', {'form': form, 'role': role})


def admin_login(request):
    return role_login(request, 'admin')


def faculty_login(request):
    return role_login(request, 'faculty')


def student_login(request):
    return role_login(request, 'student')


@login_required
def home(request):
    ensure_default_user()
    
    user_role = get_user_role(request.user)

    subjects = []
    selected_subject = None

    if user_role == 'student':
        students = Student.objects.filter(user=request.user).order_by('name')
    elif user_role == 'faculty':
        subjects = get_user_subjects(request.user)
        selected_subject = get_selected_subject(request, request.user)
        if selected_subject:
            students = Student.objects.filter(course=selected_subject).order_by('name')
        else:
            students = Student.objects.filter(course__in=subjects).order_by('name')
    else:
        students = Student.objects.order_by('name')

    course_count = Student.objects.values('course').distinct().count()
    total_students = students.count()

    # Combine everything safely into the template context dictionary
    context = {
        'students': students,
        'course_count': course_count,
        'total_students': total_students,
        'role': user_role,                 # Used in HTML templates to show/hide menus
        'username': request.user.username, # Displays personal welcome name on dashboard
        'subjects': subjects,
        'selected_subject': selected_subject,
    }

    return render(request, 'home.html', context)

def signup(request):
    ensure_default_user()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            role = form.cleaned_data.get('role')
            user.userprofile.role = role
            # Save faculty course if provided
            if role == 'faculty':
                faculty_course = form.cleaned_data.get('faculty_course')
                user.userprofile.course = faculty_course
            user.userprofile.save()
            login(request, user)
            messages.success(request, 'Account created successfully. Welcome!')
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

@login_required
def add_subject(request):
    ensure_default_user()
    if get_user_role(request.user) != 'faculty':
        messages.error(request, 'Unauthorized')
        return redirect('home')

    if request.method == 'POST':
        new_subject = request.POST.get('new_subject', '').strip()
        if new_subject:
            profile = request.user.userprofile
            subjects = get_user_subjects(request.user)
            if new_subject not in subjects:
                subjects.append(new_subject)
                profile.course = ', '.join(subjects)
                profile.save()
                messages.success(request, f'Subject "{new_subject}" added.')
            else:
                messages.info(request, f'Subject "{new_subject}" is already in your list.')
            return redirect(f"{request.build_absolute_uri('/')}?subject={new_subject}")

    return redirect('home')

@login_required
def add_student(request):
    ensure_default_user()
    user_role = get_user_role(request.user)
    selected_subject = None
    if user_role == 'faculty':
        selected_subject = get_selected_subject(request, request.user)

    if request.method == 'POST':
        post_data = request.POST.copy()
        if user_role == 'faculty' and selected_subject:
            post_data['course'] = selected_subject
        form = StudentForm(post_data)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully.')
            return redirect('home')
    else:
        if user_role == 'faculty' and selected_subject:
            form = StudentForm(initial={'course': selected_subject})
        else:
            form = StudentForm()

    return render(request, 'add_student.html', {
        'form': form,
        'role': user_role,
        'selected_subject': selected_subject,
    })

@login_required
def faculty_student_profile(request, pk):
    # View a student's profile and performance for faculty
    if get_user_role(request.user) != 'faculty':
        messages.error(request, 'Unauthorized')
        return redirect('home')

    student = Student.objects.filter(pk=pk).first()
    if not student:
        messages.error(request, 'Student not found')
        return redirect('home')

    user_subjects = get_user_subjects(request.user)
    if student.course not in user_subjects:
        messages.error(request, 'You do not have permission to view this student')
        return redirect('home')

    subjects = get_faculty_subject_objects(request.user)
    selected_subject_id = request.GET.get('subject')
    selected_semester = request.GET.get('semester')
    selected_year = request.GET.get('year')

    selected_subject = None
    if selected_subject_id:
        selected_subject = Subject.objects.filter(id=selected_subject_id, name__in=[s.name for s in subjects]).first()
    if not selected_subject:
        selected_subject = Subject.objects.filter(name=student.course).first() or (subjects[0] if subjects else None)

    semesters = list(range(1, 9))
    years = list(range(1, 5))

    try:
        selected_semester = int(selected_semester) if selected_semester else 1
    except (TypeError, ValueError):
        selected_semester = 1
    if selected_semester not in semesters:
        selected_semester = 1

    try:
        selected_year = int(selected_year) if selected_year else 1
    except (TypeError, ValueError):
        selected_year = 1
    if selected_year not in years:
        selected_year = 1

    selected_exam, _ = ExamMapping.objects.get_or_create(name=f"Semester {selected_semester} / Year {selected_year}")
    ledger = None
    if selected_subject and selected_exam:
        ledger = MarksLedger.objects.filter(student=student, subject=selected_subject, exam=selected_exam).first()

    return render(request, 'faculty_student_profile.html', {
        'student': student,
        'subjects': subjects,
        'selected_subject': selected_subject,
        'selected_semester': selected_semester,
        'selected_year': selected_year,
        'semesters': semesters,
        'years': years,
        'ledger': ledger,
    })


@login_required
def faculty_edit_student(request, pk):
    if get_user_role(request.user) != 'faculty':
        messages.error(request, 'Unauthorized')
        return redirect('home')

    student = Student.objects.filter(pk=pk).first()
    if not student:
        messages.error(request, 'Student not found')
        return redirect('home')

    user_subjects = get_user_subjects(request.user)
    if student.course not in user_subjects:
        messages.error(request, 'You do not have permission to edit this student')
        return redirect('home')

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully')
            return redirect('faculty_student_profile', pk=student.pk)
    else:
        form = StudentForm(instance=student)

    return render(request, 'faculty_edit_student.html', {'form': form, 'student': student})

# --- ADD THESE AT THE VERY BOTTOM OF YOUR views.py ---

@login_required
def profile_view(request):
    try:
        user_role = request.user.userprofile.role
    except UserProfile.DoesNotExist:
        user_role = 'student'
        
    return render(request, 'profile.html', {
        'role': user_role,
        'username': request.user.username,
        'email': request.user.email,
    })

@login_required
def academic_report_view(request):
    try:
        user_role = request.user.userprofile.role
    except UserProfile.DoesNotExist:
        user_role = 'student'

    student_record = None
    if user_role == 'student':
        student_record = Student.objects.filter(user=request.user).first()

    return render(request, 'academic_report.html', {
        'role': user_role,
        'username': request.user.username,
        'student': student_record,
    })

@login_required
def attendance_view(request):
    try:
        user_role = request.user.userprofile.role
    except UserProfile.DoesNotExist:
        user_role = 'student'

    return render(request, 'attendance.html', {
        'role': user_role,
        'username': request.user.username,
    })


@login_required
def enter_grades_view(request):
    try:
        user_role = request.user.userprofile.role
    except UserProfile.DoesNotExist:
        user_role = 'student'

    if user_role != 'faculty':
        messages.error(request, 'Only faculty users can access the marks ledger.')
        return redirect('home')

    subjects = get_faculty_subject_objects(request.user)
    semesters = list(range(1, 9))
    years = list(range(1, 5))
    selected_subject_id = request.GET.get('subject')
    selected_semester = request.GET.get('semester')
    selected_year = request.GET.get('year')

    selected_subject = None
    if selected_subject_id:
        selected_subject = Subject.objects.filter(id=selected_subject_id, name__in=[s.name for s in subjects]).first()
    if not selected_subject and subjects:
        selected_subject = subjects[0]

    try:
        selected_semester = int(selected_semester) if selected_semester else 1
    except (TypeError, ValueError):
        selected_semester = 1
    if selected_semester not in semesters:
        selected_semester = 1

    try:
        selected_year = int(selected_year) if selected_year else 1
    except (TypeError, ValueError):
        selected_year = 1
    if selected_year not in years:
        selected_year = 1

    exam_name = f"Semester {selected_semester} / Year {selected_year}"
    selected_exam, _ = ExamMapping.objects.get_or_create(name=exam_name)

    if selected_subject:
        students = Student.objects.filter(course=selected_subject.name).order_by('roll_number')
    else:
        student_names = [s.name for s in subjects]
        students = Student.objects.filter(course__in=student_names).order_by('roll_number')

    student_rows = []
    if selected_subject and selected_exam:
        ledgers = MarksLedger.objects.filter(subject=selected_subject, exam=selected_exam, student__in=students).select_related('student')
        ledger_map = {ledger.student_id: ledger for ledger in ledgers}
    else:
        ledger_map = {}

    for student in students:
        student_rows.append({
            'student': student,
            'ledger': ledger_map.get(student.id),
        })

    return render(request, 'enter_grades.html', {
        'role': user_role,
        'username': request.user.username,
        'subjects': subjects,
        'selected_subject': selected_subject,
        'selected_semester': selected_semester,
        'selected_year': selected_year,
        'semesters': semesters,
        'years': years,
        'selected_exam': selected_exam,
        'student_rows': student_rows,
    })


@login_required
def save_grade(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if get_user_role(request.user) != 'faculty':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    student_id = request.POST.get('student_id')
    subject_id = request.POST.get('subject_id')
    exam_id = request.POST.get('exam_id')
    obtained_marks = request.POST.get('obtained_marks')

    if not (student_id and subject_id and exam_id and obtained_marks is not None):
        return JsonResponse({'error': 'Missing required data.'}, status=400)

    try:
        obtained_marks = int(obtained_marks)
    except ValueError:
        return JsonResponse({'error': 'Marks must be an integer.'}, status=400)

    student = Student.objects.filter(id=student_id).first()
    subject = Subject.objects.filter(id=subject_id).first()
    exam = ExamMapping.objects.filter(id=exam_id).first()

    if not student or not subject or not exam:
        return JsonResponse({'error': 'Invalid student, subject, or exam.'}, status=400)

    if obtained_marks > subject.max_marks:
        return JsonResponse({'error': f'Cannot exceed max marks ({subject.max_marks}).'}, status=400)

    if subject.name not in get_user_subjects(request.user):
        return JsonResponse({'error': 'Unauthorized subject.'}, status=403)

    ledger, _ = MarksLedger.objects.get_or_create(
        student=student,
        subject=subject,
        exam=exam,
        defaults={'obtained_marks': obtained_marks, 'status': MarksLedger.STATUS_DRAFT}
    )
    if ledger.status == MarksLedger.STATUS_FINALIZED:
        return JsonResponse({'error': 'Cannot update finalized records.'}, status=400)

    ledger.obtained_marks = obtained_marks
    ledger.status = MarksLedger.STATUS_DRAFT
    ledger.save()

    return JsonResponse({
        'success': True,
        'student_id': student.id,
        'obtained_marks': ledger.obtained_marks,
        'status': ledger.get_status_display(),
    })


@login_required
def finalize_grades(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if get_user_role(request.user) != 'faculty':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    subject_id = request.POST.get('subject_id')
    exam_id = request.POST.get('exam_id')

    subject = Subject.objects.filter(id=subject_id).first()
    exam = ExamMapping.objects.filter(id=exam_id).first()

    if not subject or not exam:
        return JsonResponse({'error': 'Invalid subject or exam.'}, status=400)

    if subject.name not in get_user_subjects(request.user):
        return JsonResponse({'error': 'Unauthorized subject.'}, status=403)

    rows = MarksLedger.objects.filter(subject=subject, exam=exam)
    for row in rows:
        row.status = MarksLedger.STATUS_FINALIZED
        row.save()

    return JsonResponse({'success': True})