# PolyPilot — verify environment on a new Windows PC
# Usage: powershell -ExecutionPolicy Bypass -File scripts\migration\setup-new-pc.ps1

$ErrorActionPreference = "Continue"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Write-Host "PolyPilot setup check" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"
Write-Host ""

function Test-Cmd($name) {
    $ok = $null -ne (Get-Command $name -ErrorAction SilentlyContinue)
    $color = if ($ok) { "Green" } else { "Yellow" }
    Write-Host ("  [{0}] {1}" -f $(if ($ok) { "OK" } else { "!!" }), $name) -ForegroundColor $color
    return $ok
}

Write-Host "Tools:"
$hasGit = Test-Cmd "git"
$hasPy = Test-Cmd "python"

$runtimePy = Join-Path $RepoRoot "backend\.runtime\python.exe"
$hasRuntime = Test-Path $runtimePy
Write-Host ("  [{0}] backend\.runtime\python.exe" -f $(if ($hasRuntime) { "OK" } else { "!!" })) -ForegroundColor $(if ($hasRuntime) { "Green" } else { "Yellow" })

$envFile = Join-Path $RepoRoot "backend\.env"
$hasEnv = Test-Path $envFile
Write-Host ("  [{0}] backend\.env" -f $(if ($hasEnv) { "OK" } else { "!!" })) -ForegroundColor $(if ($hasEnv) { "Green" } else { "Red" })

Write-Host ""
if (-not $hasEnv) {
    Write-Host "ACTION: copy backend.env from migration backup to backend\.env" -ForegroundColor Red
    Write-Host "       or: copy backend\.env.example to backend\.env and fill POLZA_API_KEY"
}

if (-not $hasRuntime -and -not $hasPy) {
    Write-Host "ACTION: restore backend\.runtime from backup OR install Python 3.12" -ForegroundColor Yellow
}

if ($hasGit) {
    Push-Location $RepoRoot
    Write-Host ""
    Write-Host "Git:"
    git status -sb
    git log -1 --oneline
    Pop-Location
}

Write-Host ""
Write-Host "Quick test (backend):"
Write-Host "  cd backend"
Write-Host "  .\run.ps1"
Write-Host "  → http://127.0.0.1:8787/health"
Write-Host ""
Write-Host "Docs: see MIGRATION_CHECKLIST.md in repo root"
Write-Host ""
