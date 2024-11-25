@echo off

REM Activate the virtual environment (replace with your actual path)
call venv\Scripts\activate

REM Run the Django development server (adjust port if needed)
python manage.py runserver 0.0.0.0:8000