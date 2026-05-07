# Run this script after installing Git and authenticating with GitHub.
# It initializes the repository, commits all files, and pushes to origin.

Set-Location "c:\Users\Owner\OneDrive\Desktop\student management sytm\student_project"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is not installed or not available in PATH. Install Git from https://git-scm.com/download/win and reopen PowerShell."
    exit 1
}

if (-not (Test-Path .git)) {
    git init
}

git add .
git commit -m "Initial commit: fix script filename and add README"

git remote remove origin 2>$null
git remote add origin https://github.com/Jhaayush2005dev/student-database.git
git branch -M main
git push -u origin main
