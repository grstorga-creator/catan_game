@echo off
REM Catan Game - Development Environment Setup for Windows
REM This script sets up Python virtual environment, installs dependencies, and initializes git

echo.
echo ==========================================
echo Settlers of Catan - Development Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.12+ from https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Found Python:
python --version
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Git is not installed or not in PATH
    echo Install from https://git-scm.com/download/win
    echo You can continue, but git features won't work
    echo.
)

REM Create virtual environment
echo Creating Python virtual environment...
if not exist "venv" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo WARNING: pip upgrade failed, continuing anyway
)
echo.

REM Install dependencies
echo Installing Pygame...
pip install pygame --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Pygame
    pause
    exit /b 1
)
echo Pygame installed successfully
echo.

REM Initialize git repository
if not exist ".git" (
    echo Initializing git repository...
    git init
    if %errorlevel% equ 0 (
        echo Git repository initialized
    ) else (
        echo WARNING: git initialization failed (git may not be installed)
    )
) else (
    echo Git repository already initialized
)
echo.

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Your development environment is ready!
echo.
echo Next steps:
echo 1. Configure git (first time only):
echo    git config user.name "Your Name"
echo    git config user.email "your.email@example.com"
echo.
echo 2. Play the game:
echo    venv\Scripts\activate.bat
echo    python play_catan.py
echo.
echo 3. Make changes and commit:
echo    git add .
echo    git commit -m "Your message"
echo.
echo For more info, see:
echo - README.md - Overview of the project
echo - GIT_SYNC_GUIDE.md - How to sync code with git
echo - QUICK_REFERENCE.md - Quick command reference
echo.
pause
