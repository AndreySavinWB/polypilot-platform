# Настройка GitHub Actions secrets для daily CEO reminder.
# Запуск из корня репо или backend:
#   powershell -ExecutionPolicy Bypass -File backend\scripts\setup_github_secrets.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if (-not (Test-Path (Join-Path $Root ".git"))) {
    $Root = Split-Path $PSScriptRoot -Parent
}
$EnvPath = Join-Path $Root "backend\.env"
$Repo = "AndreySavinWB/polypilot-platform"
$SecretsUrl = "https://github.com/$Repo/settings/secrets/actions"
$WorkflowUrl = "https://github.com/$Repo/actions/workflows/daily-ceo-reminder.yml"

function Read-EnvValue([string]$Name) {
    if (-not (Test-Path $EnvPath)) {
        throw "Не найден $EnvPath"
    }
    foreach ($line in Get-Content $EnvPath -Encoding UTF8) {
        if ($line -match "^\s*$Name\s*=\s*(.+)\s*$") {
            return $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
    return $null
}

$botToken = Read-EnvValue "TELEGRAM_BOT_TOKEN"
$ceoChat = Read-EnvValue "TELEGRAM_CEO_CHAT_ID"
$startDate = Read-EnvValue "DAILY_PUBLISH_START_DATE"
$polzaKey = Read-EnvValue "POLZA_API_KEY"

if (-not $botToken) { throw "В backend\.env нет TELEGRAM_BOT_TOKEN" }
if (-not $ceoChat) { throw "В backend\.env нет TELEGRAM_CEO_CHAT_ID" }
if (-not $startDate) { $startDate = "2026-06-14" }
if (-not $polzaKey -or $polzaKey -eq "pza_...") {
    throw "В backend\.env нет реального POLZA_API_KEY (не заглушка pza_...)"
}

$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
    Write-Host ""
    Write-Host "GitHub CLI (gh) не установлен — secrets через UI:" -ForegroundColor Yellow
    Write-Host $SecretsUrl
    Write-Host ""
    Write-Host "Добавь 4 repository secrets (New repository secret):"
    Write-Host "  1) TELEGRAM_BOT_TOKEN      = значение из backend\.env"
    Write-Host "  2) TELEGRAM_CEO_CHAT_ID    = $ceoChat"
    Write-Host "  3) DAILY_PUBLISH_START_DATE = $startDate"
    Write-Host "  4) POLZA_API_KEY           = значение из backend\.env"
    Write-Host ""
    Write-Host "Проверка workflow:" -ForegroundColor Cyan
    Write-Host $WorkflowUrl
    Write-Host "  -> Run workflow"
    Write-Host ""
    Start-Process $SecretsUrl
    exit 0
}

Push-Location $Root
try {
    gh auth status 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Сначала: gh auth login" -ForegroundColor Yellow
        gh auth login
    }
    gh secret set TELEGRAM_BOT_TOKEN --body $botToken --repo $Repo
    gh secret set TELEGRAM_CEO_CHAT_ID --body $ceoChat --repo $Repo
    gh secret set DAILY_PUBLISH_START_DATE --body $startDate --repo $Repo
    gh secret set POLZA_API_KEY --body $polzaKey --repo $Repo
    Write-Host ""
    Write-Host "Secrets установлены." -ForegroundColor Green
    Write-Host "Проверка: открой workflow и нажми Run workflow:"
    Write-Host $WorkflowUrl
    Start-Process $WorkflowUrl
}
finally {
    Pop-Location
}
