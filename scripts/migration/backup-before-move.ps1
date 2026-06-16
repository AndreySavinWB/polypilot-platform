# PolyPilot — backup before moving to a new PC
# Usage: powershell -ExecutionPolicy Bypass -File scripts\migration\backup-before-move.ps1

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Stamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$DefaultOut = Join-Path $env:USERPROFILE "PolyPilot-Migration-Backup"
$OutRoot = if ($env:PP_BACKUP_DIR) { $env:PP_BACKUP_DIR } else { $DefaultOut }
$Dest = Join-Path $OutRoot $Stamp

New-Item -ItemType Directory -Force -Path $Dest | Out-Null

function Copy-IfExists($Src, $DstName) {
    if (Test-Path $Src) {
        $dst = Join-Path $Dest $DstName
        Copy-Item -Path $Src -Destination $dst -Recurse -Force
        return $true
    }
    return $false
}

$manifest = @()
$manifest += "PolyPilot migration backup"
$manifest += "Created: $(Get-Date -Format o)"
$manifest += "Repo: $RepoRoot"
$manifest += "Destination: $Dest"
$manifest += ""

# --- Critical: secrets ---
if (Copy-IfExists (Join-Path $RepoRoot "backend\.env") "backend.env") {
    $manifest += "[OK] backend\.env"
} else {
    $manifest += "[MISSING] backend\.env - copy manually from old PC!"
}

# --- Portable Python (not in git) ---
if (Copy-IfExists (Join-Path $RepoRoot "backend\.runtime") "backend.runtime") {
    $manifest += "[OK] backend\.runtime (portable Python)"
} else {
    $manifest += "[SKIP] backend\.runtime - install Python 3.12 on new PC"
}

# --- Git snapshot ---
Push-Location $RepoRoot
git status -sb 2>$null | Out-File (Join-Path $Dest "git-status.txt") -Encoding utf8
git log -5 --oneline 2>$null | Out-File (Join-Path $Dest "git-log.txt") -Encoding utf8
git remote -v 2>$null | Out-File (Join-Path $Dest "git-remote.txt") -Encoding utf8
Pop-Location
$manifest += "[OK] git status / log / remote"

# --- Cursor (optional) ---
$CursorUser = Join-Path $env:APPDATA "Cursor\User\settings.json"
if (Copy-IfExists $CursorUser "cursor-user-settings.json") {
    $manifest += "[OK] Cursor settings.json"
}

$SkillsSrc = Join-Path $env:USERPROFILE ".cursor\skills-cursor"
if (Copy-IfExists $SkillsSrc "cursor-skills") {
    $manifest += "[OK] Cursor skills"
}

$Transcripts = Join-Path $env:USERPROFILE ".cursor\projects\d-Andrey-PolyPilot\agent-transcripts"
if (-not (Test-Path $Transcripts)) {
    $Transcripts = Get-ChildItem (Join-Path $env:USERPROFILE ".cursor\projects") -Filter "agent-transcripts" -Recurse -Directory -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
}
if ($Transcripts -and (Copy-IfExists $Transcripts "agent-transcripts")) {
    $manifest += "[OK] Cursor agent transcripts"
}

# --- Obsidian workspace (local UI state, optional) ---
$ObsWorkspace = Join-Path $RepoRoot "PolyPilot-Штаб\.obsidian\workspace.json"
if (Copy-IfExists $ObsWorkspace "obsidian-workspace.json") {
    $manifest += "[OK] Obsidian workspace.json"
}

$manifest += ""
$manifest += "Next steps:"
$manifest += "1. Copy this folder to USB / cloud (encrypt recommended)."
$manifest += "2. git push all commits from old PC."
$manifest += "3. On new PC: git clone + restore backend.env + backend.runtime"
$manifest += "4. Read: PolyPilot-Shtab/00_Start/PEREKHOD doc (UTF-8 path in repo)"

$manifest | Out-File (Join-Path $Dest "MIGRATION_MANIFEST.txt") -Encoding utf8

Write-Host ""
Write-Host "Backup complete:" -ForegroundColor Green
Write-Host "  $Dest"
Write-Host ""
Write-Host "IMPORTANT: store backend.env securely (contains API keys)."
Write-Host ""
