# deploy_landing.ps1
# One-click deploy: creates private GitHub repo + publishes landing page to GitHub Pages
# Run from: c:\Users\229x1\Desktop\gps_attendence\landing

$env:PATH = "C:\Program Files\GitHub CLI;C:\Program Files\Git\cmd;C:\Program Files\Git\bin;" + $env:PATH

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  AI Attendance Landing Page — GitHub Pages Deployer" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Check gh auth ──────────────────────────────────────────────────
Write-Host "Step 1/6: Checking GitHub authentication..." -ForegroundColor Yellow
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in. Starting interactive login..." -ForegroundColor Red
    gh auth login --git-protocol https --web
    if ($LASTEXITCODE -ne 0) { Write-Error "GitHub login failed. Aborting."; exit 1 }
}
Write-Host "Logged in." -ForegroundColor Green

# ── Step 2: Get GitHub username ────────────────────────────────────────────
Write-Host "`nStep 2/6: Getting your GitHub username..." -ForegroundColor Yellow
$ghUser = gh api user --jq ".login" 2>&1
Write-Host "Logged in as: $ghUser" -ForegroundColor Green

# ── Step 3: Init git repo ──────────────────────────────────────────────────
Write-Host "`nStep 3/6: Initializing git repository..." -ForegroundColor Yellow
if (!(Test-Path ".git")) {
    git init
    git config user.email "deploy@snapclass.ai"
    git config user.name "SnapClass Deploy"
}

# Create .gitignore to exclude Flask server files from Pages
@"
# Flask server files (not needed for GitHub Pages static hosting)
app.py
requirements.txt
make_static.py
__pycache__/
*.pyc
templates/
"@ | Out-File -FilePath ".gitignore" -Encoding utf8

Write-Host "Git initialized." -ForegroundColor Green

# ── Step 4: Stage all static files ────────────────────────────────────────
Write-Host "`nStep 4/6: Staging files for commit..." -ForegroundColor Yellow
git add index.html static/ .gitignore
git status --short
$commitMsg = "Deploy: AI Attendance landing page - Company/Employee edition"
git commit -m $commitMsg
Write-Host "Files committed." -ForegroundColor Green

# ── Step 5: Create private GitHub repo ────────────────────────────────────
Write-Host "`nStep 5/6: Creating private GitHub repository..." -ForegroundColor Yellow
$repoName = "ai-attendance-landing"

$existing = gh repo view "$ghUser/$repoName" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Repo already exists: github.com/$ghUser/$repoName" -ForegroundColor Yellow
} else {
    gh repo create $repoName --private --description "AI Attendance System Landing Page" --source=. --remote=origin --push
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed to create repo."; exit 1 }
    Write-Host "Private repo created: github.com/$ghUser/$repoName" -ForegroundColor Green
}

# Push if not already pushed
git remote set-url origin "https://github.com/$ghUser/$repoName.git" 2>$null
git branch -M main
git push -u origin main --force

# ── Step 6: Enable GitHub Pages ────────────────────────────────────────────
Write-Host "`nStep 6/6: Enabling GitHub Pages from main branch..." -ForegroundColor Yellow

# NOTE: GitHub Pages on PRIVATE repos requires GitHub Pro/Teams plan.
# The API call below will succeed only if your account supports it.
$pagesPayload = '{"source":{"branch":"main","path":"/"}}'
$result = gh api "repos/$ghUser/$repoName/pages" --method POST --input - <<< $pagesPayload 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "GitHub Pages enabled!" -ForegroundColor Green
    $pagesUrl = "https://$ghUser.github.io/$repoName/"
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host "  LIVE URL: $pagesUrl" -ForegroundColor Green
    Write-Host "  (May take 1-3 minutes to go live)" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "GitHub Pages activation requires GitHub Pro plan for private repos." -ForegroundColor Red
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  A) Upgrade to GitHub Pro: https://github.com/settings/billing" -ForegroundColor White
    Write-Host "  B) Make repo public (free Pages): run this command:" -ForegroundColor White
    Write-Host "     gh repo edit $ghUser/$repoName --visibility public" -ForegroundColor Cyan
    Write-Host "     Then re-run this script." -ForegroundColor White
    Write-Host ""
    Write-Host "Your repo is at: https://github.com/$ghUser/$repoName" -ForegroundColor Green
}
