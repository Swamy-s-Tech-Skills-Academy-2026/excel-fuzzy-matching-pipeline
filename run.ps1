#!/usr/bin/env pwsh
# PowerShell script to run the Excel Fuzzy Matching Pipeline
# Usage: .\run.ps1

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    uv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment. Please install uv first." -ForegroundColor Red
        exit 1
    }
}

# Check if dependencies are installed
$pandasCheck = & ".venv\Scripts\python.exe" -c "import pandas" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Dependencies not installed. Installing..." -ForegroundColor Yellow
    & ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies." -ForegroundColor Red
        exit 1
    }
}

# Run the pipeline
Write-Host "Running Excel Fuzzy Matching Pipeline..." -ForegroundColor Green
& ".venv\Scripts\python.exe" run_pipeline.py

exit $LASTEXITCODE

