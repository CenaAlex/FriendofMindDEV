@echo off
cd /d "C:\Users\HF\OneDrive\Documents\FriendOfMind"
call venv\Scripts\activate.bat
python manage.py runserver
pause