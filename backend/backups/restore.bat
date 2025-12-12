@echo off
REM SaarLM Emergency Restore Script for Windows
REM Double-click this file if the app breaks

echo.
echo ======================================
echo   SaarLM Emergency Restore Script
echo ======================================
echo.
echo Restoring to last working version...
echo.

REM Navigate to project root
cd ..\..

REM Create backup of current broken files
echo Creating backup of current files...
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
mkdir backend\backups\broken_backup_%TIMESTAMP% 2>nul

copy backend\main.py backend\backups\broken_backup_%TIMESTAMP%\main.py >nul 2>&1
copy backend\services\ocr_service.py backend\backups\broken_backup_%TIMESTAMP%\ocr_service.py >nul 2>&1
copy backend\services\script_generator.py backend\backups\broken_backup_%TIMESTAMP%\script_generator.py >nul 2>&1
copy backend\services\tts_service.py backend\backups\broken_backup_%TIMESTAMP%\tts_service.py >nul 2>&1
copy frontend\src\App.jsx backend\backups\broken_backup_%TIMESTAMP%\App.jsx >nul 2>&1

echo Broken files backed up to: backend\backups\broken_backup_%TIMESTAMP%
echo.

REM Restore working files
echo Restoring working files...
copy backend\backups\main_working_v1.py backend\main.py
copy backend\backups\ocr_service_working_v1.py backend\services\ocr_service.py
copy backend\backups\script_generator_working_v1.py backend\services\script_generator.py
copy backend\backups\tts_service_working_v1.py backend\services\tts_service.py
copy backend\backups\App_working_v1.jsx frontend\src\App.jsx
copy backend\backups\.env.backup backend\.env >nul 2>&1

echo.
echo ======================================
echo   Restore Complete!
echo ======================================
echo.
echo Next steps:
echo   1. Stop any running backend servers (Ctrl+C in their windows)
echo   2. Start backend with:
echo      cd backend
echo      set PYTHONIOENCODING=utf-8
echo      venv311\Scripts\python.exe -m uvicorn main:app --reload --port 8001
echo.
echo   3. Frontend should auto-reload at http://localhost:3002
echo.
echo All systems ready!
echo.
pause
