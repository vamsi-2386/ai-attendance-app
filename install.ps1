# install.ps1 — Run this instead of 'pip install -r requirements.txt' on Windows
# Fixes: webrtcvad requires C++ Build Tools (which most users don't have)
# Solution: installs the pre-built binary wheel, then resemblyzer without its deps

Write-Host "=== AI Attendance System — Dependency Installer ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Core packages (streamlit, numpy, pandas, sklearn, bcrypt, segno, pillow, librosa)
Write-Host "Step 1/3: Installing core packages..." -ForegroundColor Yellow
pip install streamlit numpy pandas scikit-learn dlib-bin setuptools"<"70.0.0 bcrypt segno pillow librosa
if ($LASTEXITCODE -ne 0) { Write-Error "Core install failed."; exit 1 }

# Step 2: Face recognition models (large download ~100MB from GitHub)
Write-Host "`nStep 2/3: Installing face recognition models (large download)..." -ForegroundColor Yellow
pip install git+https://github.com/ageitgey/face_recognition_models
if ($LASTEXITCODE -ne 0) { Write-Error "Face models install failed."; exit 1 }

# Step 3: Voice recognition — webrtcvad-wheels MUST come before resemblyzer
Write-Host "`nStep 3/3: Installing voice recognition (webrtcvad-wheels + resemblyzer)..." -ForegroundColor Yellow
pip install webrtcvad-wheels
if ($LASTEXITCODE -ne 0) { Write-Error "webrtcvad-wheels install failed."; exit 1 }

pip install resemblyzer --no-deps
if ($LASTEXITCODE -ne 0) { Write-Error "resemblyzer install failed."; exit 1 }

Write-Host "`n=== All dependencies installed successfully! ===" -ForegroundColor Green
Write-Host "Run the app with: streamlit run app.py" -ForegroundColor Cyan
