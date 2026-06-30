# Nemory dev launcher.
#   .\run.ps1                  -> http://127.0.0.1:8000 (opens the browser)
#   .\run.ps1 -Port 5050       -> use a different port
#   .\run.ps1 -HostAddress 0.0.0.0 -> expose on the local network (test on a phone)
#   .\run.ps1 -NoBrowser       -> don't open the browser

param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1",
    [switch]$NoBrowser
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

# A browser can't reach 0.0.0.0 — point it at localhost instead.
$browseHost = if ($HostAddress -eq "0.0.0.0") { "127.0.0.1" } else { $HostAddress }
$url = "http://${browseHost}:${Port}"

# Open the browser a couple seconds after the server starts (it blocks below).
if (-not $NoBrowser) {
    Start-Job -ScriptBlock {
        param($u)
        Start-Sleep -Seconds 2
        Start-Process $u
    } -ArgumentList $url | Out-Null
}

Write-Host "Starting Nemory on $url" -ForegroundColor Green
flask --app wsgi run --debug --host $HostAddress --port $Port
