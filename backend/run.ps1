$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".runtime\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Portable Python not found. Run setup from README or re-download .runtime/python.exe"
    exit 1
}

Set-Location $Root
& $Python (Join-Path $Root "server.py")
