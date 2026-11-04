# start-dev.ps1 - Launches both Backend and Frontend servers

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Starting Book API Full-Stack Services" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Start FastAPI Backend on port 8000
Write-Host "`n[1/2] Starting FastAPI Backend (http://127.0.0.1:8000)..." -ForegroundColor Yellow
Start-Process powershell -WorkingDirectory $PSScriptRoot -ArgumentList "-NoExit", "-Command", "python -m uvicorn book_cache.main:app --reload"

# 2. Start React Frontend on port 5173
Write-Host "[2/2] Starting React Frontend (http://localhost:5173)..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory "$PSScriptRoot\frontend" -ArgumentList "-NoExit", "-Command", "npm run dev"

Write-Host "`n✅ Both servers are running in separate windows!" -ForegroundColor Green
Write-Host "Backend Docs: http://127.0.0.1:8000/docs" -ForegroundColor DarkGray
Write-Host "Frontend App: http://localhost:5173" -ForegroundColor DarkGray