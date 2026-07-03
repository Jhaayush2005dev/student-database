import os
from pathlib import Path


def get_database_path():
    if os.getenv('VERCEL') or os.getenv('VERCEL_ENV'):
        return '/tmp/student_project.sqlite3'
    return str(Path(__file__).resolve().parent.parent / 'db.sqlite3')
