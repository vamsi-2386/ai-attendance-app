# ============================================================
#  Lumenor AI Attendance Platform — Start Script
#  Kills stale processes, clears cache, starts fresh.
# ============================================================

Set-Location -Path $PSScriptRoot

# ── 0. Check and Install Dependencies ───────────────────────
Write-Host "Checking dependencies..." -ForegroundColor Cyan
python -c "import streamlit, face_recognition, webrtcvad" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Dependencies missing. Running install script..." -ForegroundColor Yellow
    .\install.ps1
} else {
    Write-Host "Dependencies found." -ForegroundColor Green
}


# ── 1. Kill any existing Python / Streamlit processes ───────
Write-Host "Stopping any running instances..." -ForegroundColor Yellow
Get-Process python*   -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process streamlit* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# ── 2. Clear Python bytecode cache ──────────────────────────
Write-Host "Clearing bytecode cache..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Include "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# ── 3. Set environment ───────────────────────────────────────
$env:PYTHONPATH = $PSScriptRoot

# ── 4. Start Flask landing page ──────────────────────────────
Write-Host "Starting Landing Page on port 5002..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "landing.py"

# ── 5. Start Streamlit app ───────────────────────────────────
Write-Host "Starting Lumenor AI App on port 8501..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m streamlit run app.py --server.port 8501 --server.headless true --server.runOnSave true"

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "=======================================" -ForegroundColor Magenta
Write-Host "  LUMENOR AI ATTENDANCE PLATFORM" -ForegroundColor Magenta
Write-Host "=======================================" -ForegroundColor Magenta
Write-Host "  Landing Page : http://127.0.0.1:5002" -ForegroundColor White
Write-Host "  App Portal   : http://localhost:8501"  -ForegroundColor White
Write-Host "=======================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "Press Ctrl+C to stop all services." -ForegroundColor Gray

# Keep the window open so processes don't die
Wait-Process -Name "python" -ErrorAction SilentlyContinue
