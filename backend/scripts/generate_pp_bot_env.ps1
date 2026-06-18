# Генерирует PP_BOT_ENV для Railway (одна переменная вместо четырёх).
# Usage: powershell -File backend\scripts\generate_pp_bot_env.ps1

$ErrorActionPreference = "Stop"
$EnvPath = Join-Path $PSScriptRoot "..\.env"
if (-not (Test-Path $EnvPath)) { throw "Нет $EnvPath" }

$Keys = @(
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CEO_CHAT_ID",
    "PUBLIC_BACKEND_URL",
    "CEO_BRIEF_SECRET",
    "DAILY_PUBLISH_START_DATE",
    "TELEGRAM_CHANNEL_URL",
    "TELEGRAM_WEBHOOK_SECRET"
)

$lines = New-Object System.Collections.Generic.List[string]
foreach ($line in Get-Content $EnvPath -Encoding UTF8) {
    if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=') {
        $name = $Matches[1]
        if ($Keys -contains $name) {
            $lines.Add($line.Trim())
        }
    }
}

if ($lines.Count -eq 0) { throw "В .env нет telegram-переменных" }

$block = ($lines -join "`n")
$bytes = [Text.Encoding]::UTF8.GetBytes($block)
$b64 = [Convert]::ToBase64String($bytes)

Write-Host ""
Write-Host "Railway -> Variables -> + New Variable" -ForegroundColor Cyan
Write-Host "  Name:  PP_BOT_ENV"
Write-Host "  Value: (скопируй строку ниже)"
Write-Host ""
Write-Host $b64
Write-Host ""
Write-Host "Затем Deployments -> Redeploy" -ForegroundColor Yellow
