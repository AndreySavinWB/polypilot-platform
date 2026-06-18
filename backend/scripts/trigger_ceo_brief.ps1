# Отправить утренний бриф CEO через Railway (обходит блокировку api.telegram.org на ПК)
# Usage: .\scripts\trigger_ceo_brief.ps1
# Требует в Railway: TELEGRAM_BOT_TOKEN, TELEGRAM_CEO_CHAT_ID, CEO_BRIEF_SECRET

$ErrorActionPreference = "Stop"
$BackendRoot = Split-Path $PSScriptRoot -Parent
$EnvFile = Join-Path $BackendRoot ".env"
$RailwayUrl = "https://polypilot-platform-production.up.railway.app"
$Key = "pp-ceo-morning-2026"

if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*CEO_BRIEF_SECRET=(.+)$') { $Key = $Matches[1].Trim() }
        if ($_ -match '^\s*PUBLIC_BACKEND_URL=(.+)$') {
            $u = $Matches[1].Trim()
            if ($u) { $RailwayUrl = $u.TrimEnd('/') }
        }
    }
}

$Uri = "$RailwayUrl/api/ceo/brief/send?key=$Key"
Write-Host "GET $Uri"
try {
    $resp = Invoke-RestMethod -Uri $Uri -Method Get -TimeoutSec 60
    Write-Host "OK:" ($resp | ConvertTo-Json -Compress)
} catch {
    Write-Host "FAILED:" $_.Exception.Message
    Write-Host ""
    Write-Host "Railway -> Variables:"
    Write-Host "  TELEGRAM_BOT_TOKEN, TELEGRAM_CEO_CHAT_ID, CEO_BRIEF_SECRET=$Key"
    Write-Host "Redeploy backend after git push."
    exit 1
}
