# Catan Game - Development Environment Setup for Windows (PowerShell)

Write-Host ""
Write-Host "=========================================="
Write-Host "Settlers of Catan - Development Setup"
Write-Host "=========================================="
Write-Host ""

# Check Python
$pythonCheck = Invoke-Expression "python --version" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH!"
    Write-Host "Install from https://www.python.org/downloads/"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Found Python: $pythonCheck"
Write-Host ""

# Create venv
Write-Host "Creating Python virtual environment..."
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "Virtual environment created"
} else {
    Write-Host "Virtual environment already exists"
}
Write-Host ""

# Activate venv
Write-Host "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip -q
Write-Host ""

# Install pygame
Write-Host "Installing Pygame..."
pip install pygame -q
Write-Host "Pygame installed"
Write-Host ""

# Init git
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..."
    git init
} else {
    Write-Host "Git repository already initialized"
}
Write-Host ""

Write-Host "=========================================="
Write-Host "Setup Complete!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Your development environment is ready!"
Write-Host ""
Read-Host "Press Enter to exit"
