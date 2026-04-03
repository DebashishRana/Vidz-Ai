param(
    [int]$Port = 8000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..")

Push-Location $repoRoot
try {
    $branch = git branch --show-current
    if ($branch -ne "main") {
        throw "Current branch is '$branch'. Switch to 'main' before running backend in main-only mode."
    }

    Write-Host "Branch check passed: main"
    Write-Host "Starting backend from app.main:app on port $Port"

    Set-Location (Join-Path $repoRoot "backend")
    uvicorn app.main:app --host 0.0.0.0 --port $Port --reload
}
finally {
    Pop-Location
}
