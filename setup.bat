@echo off
REM AI MOOC Interview & Assessment System - Setup Script

echo.
echo ====================================
echo AI MOOC Setup Script
echo ====================================
echo.

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    exit /b 1
)

echo Python: OK
echo Node.js: OK
echo.

REM Setup Backend
echo ====================================
echo Setting up Backend...
echo ====================================
cd backend

if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo Please update backend\.env with your API keys
)

echo Backend setup complete!
echo.
cd ..

REM Setup Frontend
echo ====================================
echo Setting up Frontend...
echo ====================================
cd frontend

echo Installing Node dependencies...
npm install

if not exist .env (
    echo Creating .env file...
    copy .env.example .env
)

echo Frontend setup complete!
echo.
cd ..

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo To run the application:
echo.
echo Terminal 1 - Backend:
echo   cd backend
echo   venv\Scripts\activate
echo   python -m uvicorn app.main:app --reload
echo.
echo Terminal 2 - Frontend:
echo   cd frontend
echo   npm run dev
echo.
echo Then open http://localhost:3000
echo.
echo Demo Credentials:
echo   Email: demo@example.com
echo   Password: demo1234
echo.
