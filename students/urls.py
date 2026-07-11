from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('login/faculty/', views.faculty_login, name='faculty_login'),
    path('login/student/', views.student_login, name='student_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # --- YOUR EXISTING DASHBOARD ROUTES ---
    path('', views.home, name='home'),
    path('add/', views.add_student, name='add_student'),

    # --- NEW FUNCTIONAL SIDEBAR ROUTES ---
    path('profile/', views.profile_view, name='profile'),
    path('academic-report/', views.academic_report_view, name='academic_report'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('enter-grades/', views.enter_grades_view, name='enter_grades'),
    path('enter-grades/save/', views.save_grade, name='save_grade'),
    path('enter-grades/finalize/', views.finalize_grades, name='finalize_grades'),
    path('faculty/student/<int:pk>/', views.faculty_student_profile, name='faculty_student_profile'),
    path('faculty/student/<int:pk>/edit/', views.faculty_edit_student, name='faculty_edit_student'),
    path('faculty/add-subject/', views.add_subject, name='add_subject'),
]