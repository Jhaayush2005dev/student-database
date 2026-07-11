from pathlib import Path
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from student_project.bootstrap import get_database_path
from .models import Student


class DatabaseBootstrapTests(SimpleTestCase):
    def test_uses_temp_db_path_on_vercel(self):
        with patch.dict('os.environ', {'VERCEL': '1'}, clear=False):
            self.assertEqual(get_database_path(), '/tmp/student_project.sqlite3')

    def test_uses_project_db_path_locally(self):
        with patch.dict('os.environ', {'VERCEL': ''}, clear=False):
            self.assertEqual(get_database_path(), str(Path(__file__).resolve().parent.parent / 'db.sqlite3'))


class StudentRoleDashboardTests(TestCase):
    def test_student_sees_their_own_details_and_marks(self):
        user = User.objects.create_user(username='student1', password='pass123')
        user.userprofile.role = 'student'
        user.userprofile.save()

        student = Student.objects.create(
            user=user,
            name='Alice Johnson',
            roll_number='1001',
            email='alice@example.com',
            course='Computer Science',
            date_of_birth='2000-01-01',
            marks=88,
        )

        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('academic_report'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, student.name)
        self.assertContains(response, '88')
        self.assertContains(response, student.course)
