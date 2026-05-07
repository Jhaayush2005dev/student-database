# Student Database

A simple Django student management system for adding and viewing student records.

## Features

- Add student name, roll number, email, course, and date of birth
- View all students in a dashboard
- Uses SQLite for local development

## Setup

```powershell
python -m venv env
env\Scripts\Activate.ps1
pip install django
python manage.py migrate
python manage.py runserver
```

## Notes

- Fixed a static file naming issue (`sctipt.js` renamed to `script.js`)
- Added `.gitignore` to exclude environment files and local database
