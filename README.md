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

This project is configured for Docker-based deployment, including Vercel.

### Files added for deployment

- `requirements.txt`
- `Dockerfile`
- `vercel.json`
- `.dockerignore`

### Production environment variables

Set these in your deployment platform:

- `DJANGO_SECRET_KEY`
- `DEBUG=False`
- `DJANGO_ALLOWED_HOSTS` (for example: `your-app.vercel.app`)
- `DATABASE_URL` (recommended for production; otherwise SQLite is used locally)

### Deploy on Vercel with Docker

1. Connect the GitHub repo to Vercel.
2. Ensure the branch is `main`.
3. Add environment variables via the Vercel dashboard.
4. Deploy.

## Notes

- Fixed a static file naming issue (`sctipt.js` renamed to `script.js`).
- Added production-ready static file support with WhiteNoise.
