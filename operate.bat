@echo off

REM Activate the virtual environment
call venv\Scripts\activate

REM Run the Django development server
python manage.py runserver 127.0.0.1:8000