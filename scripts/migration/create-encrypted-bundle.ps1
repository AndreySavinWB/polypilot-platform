# Creates AES-256 encrypted migration bundle for GitHub (no plain secrets in git).
# Usage:
#   $env:PP_MIGRATION_PASSWORD = "your-long-password"
#   powershell -ExecutionPolicy Bypass -File scripts\migration\create-encrypted-bundle.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$OutDir = Join-Path $RepoRoot "migration\encrypted"
$BundleZip = Join-Path $env:TEMP "polypilot-migration-bundle.zip"
$OutEnc = Join-Path $OutDir "polypilot-migration.enc"
$OutMeta = Join-Path $OutDir "polypilot-migration.meta.json"

$Password = $env:PP_MIGRATION_PASSWORD
if (-not $Password -or $Password.Length -lt 12) {
    Write-Error "Set PP_MIGRATION_PASSWORD (min 12 chars) before running."
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
if (Test-Path $BundleZip) { Remove-Item $BundleZip -Force }

$Stage = Join-Path $env:TEMP "pp-migration-stage"
if (Test-Path $Stage) { Remove-Item $Stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $Stage | Out-Null

function Stage-Path($Rel, $Src) {
    if (-not (Test-Path $Src)) {
        Write-Warning "Skip missing: $Src"
        return
    }
    $dst = Join-Path $Stage $Rel
    $parent = Split-Path $dst -Parent
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    if (Test-Path $Src -PathType Container) {
        Copy-Item $Src $dst -Recurse -Force
    } else {
        Copy-Item $Src $dst -Force
    }
    Write-Host "  + $Rel"
}

Write-Host "Staging files..."
Stage-Path "backend\.env" (Join-Path $RepoRoot "backend\.env")
Stage-Path "backend\.runtime" (Join-Path $RepoRoot "backend\.runtime")

$cursorSettings = Join-Path $env:APPDATA "Cursor\User\settings.json"
Stage-Path "cursor\settings.json" $cursorSettings

$skills = Join-Path $env:USERPROFILE ".cursor\skills-cursor"
Stage-Path "cursor\skills-cursor" $skills

$manifest = @(
    "PolyPilot encrypted migration bundle",
    "Created: $(Get-Date -Format o)",
    "Restore: scripts\migration\restore-from-github.ps1"
)
$manifest | Out-File (Join-Path $Stage "README-restore.txt") -Encoding utf8

Write-Host "Compressing..."
if (Test-Path $BundleZip) { Remove-Item $BundleZip -Force }
Compress-Archive -Path (Join-Path $Stage "*") -DestinationPath $BundleZip -CompressionLevel Optimal

Write-Host "Encrypting..."
$plain = [IO.File]::ReadAllBytes($BundleZip)
$salt = New-Object byte[] 16
$iv = New-Object byte[] 16
$rng = [Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($salt)
$rng.GetBytes($iv)

$derive = New-Object Security.Cryptography.Rfc2898DeriveBytes($Password, $salt, 200000, [Security.Cryptography.HashAlgorithmName]::SHA256)
$key = $derive.GetBytes(32)

$aes = [Security.Cryptography.Aes]::Create()
$aes.Mode = [Security.Cryptography.CipherMode]::CBC
$aes.Padding = [Security.Cryptography.PaddingMode]::PKCS7
$aes.Key = $key
$aes.IV = $iv

$encryptor = $aes.CreateEncryptor()
$cipher = $encryptor.TransformFinalBlock($plain, 0, $plain.Length)
[IO.File]::WriteAllBytes($OutEnc, $cipher)

$meta = @{
    version = 1
    algorithm = "AES-256-CBC"
    kdf = "PBKDF2-SHA256"
    iterations = 200000
    saltBase64 = [Convert]::ToBase64String($salt)
    ivBase64 = [Convert]::ToBase64String($iv)
    created = (Get-Date -Format o)
    plainSizeBytes = $plain.Length
    cipherSizeBytes = $cipher.Length
} | ConvertTo-Json -Depth 3
$meta | Out-File $OutMeta -Encoding utf8

Remove-Item $Stage -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $BundleZip -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Encrypted bundle ready:" -ForegroundColor Green
Write-Host "  $OutEnc"
Write-Host "  $OutMeta"
Write-Host ""
Write-Host "Commit and push migration/encrypted/ to GitHub."
Write-Host "Password is NOT stored in git - save it separately."
if ($env:PP_MIGRATION_PASSWORD_FILE) {
    $env:PP_MIGRATION_PASSWORD | Out-File $env:PP_MIGRATION_PASSWORD_FILE -Encoding utf8 -NoNewline
    Write-Host "Password saved locally (gitignored): $env:PP_MIGRATION_PASSWORD_FILE"
}
