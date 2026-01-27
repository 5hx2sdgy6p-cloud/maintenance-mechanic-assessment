@echo off
REM ========================================
REM Maintenance Assessment - Advanced Startup
REM ========================================

echo.
echo ========================================
echo  MAINTENANCE ASSESSMENT APPLICATION
echo ========================================
echo.

REM Change to the project directory
REM IMPORTANT: Update this path to match your actual project location
cd /d C:\github-repo

REM Check if directory exists
if not exist package.json (
    echo ERROR: Project directory not found!
    echo Please update the path in this batch file.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist node_modules (
    echo Node modules not found. Installing dependencies...
    echo This may take a few minutes...
    echo.
    npm install
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        echo Make sure Node.js and npm are installed
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
)

echo Starting React application...
echo.
echo ========================================
echo.

REM Start the React development server
npm start

REM If npm start fails, keep window open to see error
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Failed to start the application
    echo ========================================
    pause
)
