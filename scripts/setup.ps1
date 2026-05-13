# One-shot pre-workshop setup for Windows.
# Run from the repo root in PowerShell:
#   .\scripts\setup.ps1
#
# Idempotent: re-running is safe.

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "=== Azure AI Foundry v2 Workshop — Pre-Setup ===" -ForegroundColor Cyan
Write-Host ""

# 1. Python version check
$pyVersion = (python --version) 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found on PATH. Install Python 3.11 or 3.12 first: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}
Write-Host "✓ $pyVersion"

# 2. .env file
if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "✓ Created .env from .env.example"
} else {
    Write-Host "✓ .env already exists"
}

# 3. Virtualenv
if (-not (Test-Path ".venv")) {
    Write-Host "→ Creating virtual environment .venv ..."
    python -m venv .venv
}
Write-Host "✓ .venv ready"

# 4. Activate venv for this session
& .\.venv\Scripts\Activate.ps1
Write-Host "✓ venv activated"

# 5. Upgrade pip
Write-Host "→ Upgrading pip ..."
python -m pip install --upgrade pip --quiet

# 6. Install all lab requirements
$reqs = @(
    "shared/requirements.txt",
    "lab1-multi-agent-maf/requirements.txt",
    "lab2-mcp-connect/requirements.txt",
    "lab3-deploy-observe/requirements.txt",
    "lab4-eval-teams/requirements.txt"
)
foreach ($r in $reqs) {
    Write-Host "→ pip install -r $r"
    pip install -r $r --quiet
}
Write-Host "✓ All Python dependencies installed"

# 7. Pre-cache the MCP server used by Lab 2
Write-Host "→ Pre-caching Lab 2 MCP server (npx) ..."
try {
    npx -y @modelcontextprotocol/server-everything --help *> $null
    Write-Host "✓ Lab 2 MCP server cached"
} catch {
    Write-Host "⚠️  npx not found or failed — install Node.js 18+ before the workshop" -ForegroundColor Yellow
}

# 8. Verify
Write-Host ""
Write-Host "=== Running verify_setup.py ===" -ForegroundColor Cyan
python shared/verify_setup.py

Write-Host ""
Write-Host "Done. You're ready for the workshop." -ForegroundColor Green
Write-Host "On workshop day: activate the venv, paste endpoints into .env, run verify_setup.py once more, then start Lab 1." -ForegroundColor Green
