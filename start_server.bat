@echo off
cd /d "C:\Users\markl\FriendofMindDEV"
call venv\Scripts\activate.bat
python manage.py runserver
pause