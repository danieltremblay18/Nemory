# Nemory dev launcher.
#   .\run.ps1            -> http://127.0.0.1:8000
#   .\run.ps1 -Port 5050 -> use a different port
#   .\run.ps1 -Host 0.0.0.0 -> expose on the local network (test on a phone)

param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

# Activate the virtual environment if one exists.
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

# Create the database on first run.
if (-not (Test-Path "instance\nemory.sqlite")) {
    Write-Host "First run: initializing the database..." -ForegroundColor Cyan
    flask --app wsgi init-db
}

Write-Host "Starting Nemory on http://${HostAddress}:${Port}" -ForegroundColor Green
flask --app wsgi run --debug --host $HostAddress --port $Port
