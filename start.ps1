# IntelliScore AI – Startup Script (Windows PowerShell)
# Run this from the intelliscore-ai directory:
#   .\start.ps1
#
# This starts:
#   1. FastAPI backend  (http://localhost:8000)
#   2. Streamlit frontend  (http://localhost:8501)

$Root = $PSScriptRoot
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
$VenvUvicorn = Join-Path $Root ".venv\Scripts\uvicorn.exe"
$VenvStreamlit = Join-Path $Root ".venv\Scripts\streamlit.exe"

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  IntelliScore AI  |  Starting services..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. FastAPI backend ────────────────────────────────────────────────────────
Write-Host "▶  Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Green
$backendDir = Join-Path $Root "backend"
Start-Process -FilePath "powershell.exe" -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$backendDir'; & '$VenvUvicorn' app.main:app --reload --host 0.0.0.0 --port 8000"
) -WindowStyle Normal

Start-Sleep -Seconds 2

# ── 2. Streamlit frontend ─────────────────────────────────────────────────────
Write-Host "▶  Starting Streamlit frontend on http://localhost:8501 ..." -ForegroundColor Green
$frontendDir = Join-Path $Root "frontend\streamlit_app"
Start-Process -FilePath "powershell.exe" -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$frontendDir'; & '$VenvStreamlit' run Home.py --server.port 8501 --server.headless false"
) -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  ✅  Both services are starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend  → http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  Frontend → http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "  TIP: If the backend is unavailable, use the" -ForegroundColor Gray
Write-Host "  '🎮 Try Demo' button on the Login page." -ForegroundColor Gray
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Open Streamlit in browser
Start-Sleep -Seconds 4
Start-Process "http://localhost:8501"
