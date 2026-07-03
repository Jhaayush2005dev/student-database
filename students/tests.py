from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from student_project.bootstrap import get_database_path


class DatabaseBootstrapTests(SimpleTestCase):
    def test_uses_temp_db_path_on_vercel(self):
        with patch.dict('os.environ', {'VERCEL': '1'}, clear=False):
            self.assertEqual(get_database_path(), '/tmp/student_project.sqlite3')

    def test_uses_project_db_path_locally(self):
        with patch.dict('os.environ', {'VERCEL': ''}, clear=False):
            self.assertEqual(get_database_path(), str(Path(__file__).resolve().parent.parent / 'db.sqlite3'))
