$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = Join-Path $Root ".runtime\python.exe"
$Script = Join-Path $Root "scripts\harvest_test_events.py"

Set-Location $Root
& $Python $Script
