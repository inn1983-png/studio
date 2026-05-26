Write-Host "=== Txtovideo Studio 本地开发环境 ===" -ForegroundColor Cyan

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue

if (-not $pythonCmd) {
    Write-Host "[ERROR] Python not found. Please install Python 3.12+" -ForegroundColor Red
    exit 1
}
if (-not $nodeCmd) {
    Write-Host "[ERROR] Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Python: $($pythonCmd.Source)" -ForegroundColor Green
Write-Host "[OK] Node.js: $($nodeCmd.Source)" -ForegroundColor Green

Write-Host "`n--- Starting Backend ---" -ForegroundColor Yellow
Set-Location "$PSScriptRoot\..\backend"
if (Test-Path "venv\Scripts\Activate.ps1") {
    & venv\Scripts\Activate.ps1
}
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "src.main:app", "--reload", "--port", "8000" -NoNewWindow

Write-Host "`n--- Starting Frontend ---" -ForegroundColor Yellow
Set-Location "$PSScriptRoot\..\frontend"
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -NoNewWindow

Write-Host "`n=== Services Starting ===" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`nPress Ctrl+C to stop all services" -ForegroundColor Yellow
