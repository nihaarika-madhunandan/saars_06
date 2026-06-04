#!/usr/bin/env powershell
# ResQPaws - Quick Start Setup Script
# Run this script to set up and start the application

param(
    [switch]$Install = $false,
    [switch]$Seed = $false,
    [switch]$CleanDB = $false
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  ResQPaws - Quick Start Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPath = Join-Path $scriptDir ".venv"
if (-not (Test-Path $venvPath)) {
    $venvPath = Join-Path $scriptDir "venv"
}
$activateScript = "$venvPath\Scripts\Activate.ps1"

# Step 1: Activate virtual environment
if (Test-Path $activateScript) {
    Write-Host "[1/4] 📦 Activating virtual environment..." -ForegroundColor Yellow
    & $activateScript
    Write-Host "      ✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "[1/4] ❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "      Run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Step 2: Upgrade pip and install requirements
if ($Install) {
    Write-Host "[2/4] 📚 Installing/upgrading packages..." -ForegroundColor Yellow
    & "$venvPath\Scripts\python.exe" -m pip install --upgrade pip
    & "$venvPath\Scripts\python.exe" -m pip install -r requirements.txt
    Write-Host "      ✅ Packages installed" -ForegroundColor Green
} else {
    Write-Host "[2/4] ⏭️  Skipping package installation (use -Install flag to upgrade)" -ForegroundColor Yellow
}

# Step 3: Clean database if requested
if ($CleanDB) {
    Write-Host "[3/4] 🗑️  Cleaning database..." -ForegroundColor Yellow
    $dbPath = "$scriptDir\instance\resqpaws.db"
    if (Test-Path $dbPath) {
        Remove-Item $dbPath
        Write-Host "      ✅ Database removed" -ForegroundColor Green
    }
} else {
    Write-Host "[3/4] ⏭️  Keeping existing database" -ForegroundColor Yellow
}

# Step 4: Start the application
Write-Host "[4/4] 🚀 Starting ResQPaws application..." -ForegroundColor Yellow
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Application is running!" -ForegroundColor Green
Write-Host "  🌐 Open: http://localhost:5000" -ForegroundColor Green
Write-Host "  🛑 Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

& "$venvPath\Scripts\python.exe" app.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Application failed to start" -ForegroundColor Red
    Write-Host "   Check the error messages above" -ForegroundColor Yellow
    Write-Host "   Try running with -Install -CleanDB flags" -ForegroundColor Yellow
}
