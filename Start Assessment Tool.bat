@echo off
title Maintenance Assessment Tool Launcher

echo ============================================================
echo    MAINTENANCE MECHANIC ASSESSMENT TOOL
echo    Simply Works AI
echo ============================================================
echo.

:: Change to the project directory
cd /d C:\github-repo

echo Starting Python backend server...
echo.

:: Start Python backend in a new window
start "Assessment Backend - Port 5000" cmd /k "cd /d C:\github-repo && python assessment_backend.py"

:: Wait a moment for the backend to start
echo Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

echo.
echo Starting React frontend...
echo.

:: Start React app in a new window
start "Assessment Frontend - Port 3000" cmd /k "cd /d C:\github-repo && npm start"

echo.
echo ============================================================
echo    BOTH SERVERS ARE STARTING!
echo ============================================================
echo.
echo    Backend:  http://localhost:5000  (Python/Flask)
echo    Frontend: http://localhost:3000  (React)
echo.
echo    Your browser should open automatically.
echo.
echo    To stop the servers, close both command windows
echo    or press Ctrl+C in each window.
echo ============================================================
echo.
echo You can close this window now.
echo.
pause
