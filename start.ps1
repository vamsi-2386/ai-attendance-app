Set-Location -Path $PSScriptRoot

Write-Host "Starting Landing Page (Flask) on port 5002..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "landing.py"

Write-Host "Starting AI Attendance App (Streamlit) on port 8501..." -ForegroundColor Green
$env:PYTHONPATH="."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m streamlit run app.py"

Write-Host "Both services are starting up!" -ForegroundColor Yellow
Write-Host "Landing Page: http://127.0.0.1:5002"
Write-Host "App Portal: http://localhost:8501"
