import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','student_project.settings')
django.setup()
from django.contrib.auth.models import User
from students.models import UserProfile

u, created = User.objects.get_or_create(username='admin', defaults={'email':'admin@example.com'})
if not u.is_superuser or not u.is_staff:
    u.is_superuser = True
    u.is_staff = True
    u.set_password('admin123')
    u.save()
# ensure profile exists and has role admin
try:
    prof = u.userprofile
    prof.role = 'admin'
    prof.save()
except Exception:
    UserProfile.objects.create(user=u, role='admin')

print('admin OK', u.username, u.is_superuser)
