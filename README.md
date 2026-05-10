# Student Database

A simple Django student management system for adding and viewing student records.

## Features

- Add student name, roll number, email, course, and date of birth
- View all students in a dashboard
- Uses SQLite for local development

## Local setup

```powershell
python -m venv env
env\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Deployment

This project is configured for serverless Python deployment on Vercel.

### Deploy on Vercel

1. Go to https://vercel.com/new and import the `student-database` repository.
2. Add environment variables:
   - `DJANGO_SECRET_KEY` - random secure string
   - `DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS` - your Vercel domain (e.g., `your-app.vercel.app`)
3. Click **Deploy** and wait for completion.

### Files used for deployment

- `api/index.py` - serverless entry point
- `vercel.json` - Vercel configuration
- `requirements.txt` - dependencies

## Notes

- Fixed static file naming issue (`sctipt.js` → `script.js`).
- Uses WhiteNoise for static file serving.
- SQLite database resets on redeploy; use `DATABASE_URL` for persistence.
- Added production-ready settings for Vercel.
- Added production-ready static file support with WhiteNoise.
