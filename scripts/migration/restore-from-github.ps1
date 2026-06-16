# Restores backend/.env and .runtime from encrypted bundle in repo.
# Usage:
#   $env:PP_MIGRATION_PASSWORD = "your-password"
#   powershell -ExecutionPolicy Bypass -File scripts\migration\restore-from-github.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Enc = Join-Path $RepoRoot "migration\encrypted\polypilot-migration.enc"
$Meta = Join-Path $RepoRoot "migration\encrypted\polypilot-migration.meta.json"
$BundleZip = Join-Path $env:TEMP "polypilot-migration-restore.zip"
$Stage = Join-Path $env:TEMP "pp-migration-restore"

$Password = $env:PP_MIGRATION_PASSWORD
if (-not $Password) {
    $Password = Read-Host "Migration password" -AsSecureString
    $BSTR = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password)
    try { $Password = [Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR) }
}

if (-not (Test-Path $Enc)) {
    Write-Error "Missing $Enc — run git pull first."
}

$meta = Get-Content $Meta -Raw | ConvertFrom-Json
$salt = [Convert]::FromBase64String($meta.saltBase64)
$iv = [Convert]::FromBase64String($meta.ivBase64)
$cipher = [IO.File]::ReadAllBytes($Enc)

$derive = New-Object Security.Cryptography.Rfc2898DeriveBytes($Password, $salt, [int]$meta.iterations, [Security.Cryptography.HashAlgorithmName]::SHA256)
$key = $derive.GetBytes(32)

$aes = [Security.Cryptography.Aes]::Create()
$aes.Mode = [Security.Cryptography.CipherMode]::CBC
$aes.Padding = [Security.Cryptography.PaddingMode]::PKCS7
$aes.Key = $key
$aes.IV = $iv

$decryptor = $aes.CreateDecryptor()
$plain = $decryptor.TransformFinalBlock($cipher, 0, $cipher.Length)

[IO.File]::WriteAllBytes($BundleZip, $plain)

if (Test-Path $Stage) { Remove-Item $Stage -Recurse -Force }
Expand-Archive -Path $BundleZip -DestinationPath $Stage -Force

$envSrc = Join-Path $Stage "backend\.env"
$runtimeSrc = Join-Path $Stage "backend\.runtime"
if (Test-Path $envSrc) {
    Copy-Item $envSrc (Join-Path $RepoRoot "backend\.env") -Force
    Write-Host "[OK] backend\.env"
} else {
    Write-Warning "backend\.env not in bundle"
}

if (Test-Path $runtimeSrc) {
    $rtDst = Join-Path $RepoRoot "backend\.runtime"
    if (Test-Path $rtDst) { Remove-Item $rtDst -Recurse -Force }
    Copy-Item $runtimeSrc $rtDst -Recurse -Force
    Write-Host "[OK] backend\.runtime"
}

$cursorSettings = Join-Path $Stage "cursor\settings.json"
if (Test-Path $cursorSettings) {
    $dst = Join-Path $env:APPDATA "Cursor\User\settings.json"
    New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
    Copy-Item $cursorSettings $dst -Force
    Write-Host "[OK] Cursor settings"
}

$skillsSrc = Join-Path $Stage "cursor\skills-cursor"
if (Test-Path $skillsSrc) {
    $skillsDst = Join-Path $env:USERPROFILE ".cursor\skills-cursor"
    Copy-Item $skillsSrc $skillsDst -Recurse -Force
    Write-Host "[OK] Cursor skills"
}

Remove-Item $Stage -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $BundleZip -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Done. Test: cd backend; .\run.ps1" -ForegroundColor Green
