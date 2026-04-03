param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [switch]$SkipFetch
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    param([string]$StartPath)

    $dir = (Resolve-Path $StartPath).Path
    while ($true) {
        if (Test-Path (Join-Path $dir ".git")) {
            return $dir
        }

        $parent = Split-Path $dir -Parent
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $dir) {
            throw "Could not find a git repository root from '$StartPath'."
        }
        $dir = $parent
    }
}

function Test-RemoteContains {
    param(
        [string]$Commit,
        [string]$RemoteBranch
    )

    $contains = git branch -r --contains $Commit 2>$null
    $matched = $contains | Where-Object { $_ -match [regex]::Escape($RemoteBranch) }
    return [bool]$matched
}

function Get-ApiFingerprint {
    param([string]$Url)

    $result = [ordered]@{
        reachable = $false
        style = "unknown"
        docsUrl = "$Url/docs"
        healthUrl = "$Url/health"
        openapiUrl = "$Url/openapi.json"
        foundPaths = @()
        healthBody = $null
    }

    try {
        $openapi = Invoke-RestMethod -Uri $result.openapiUrl -TimeoutSec 6
        $result.reachable = $true

        $paths = @($openapi.paths.PSObject.Properties.Name)
        $result.foundPaths = $paths

        $hasApiV1 = $paths | Where-Object { $_ -like "/api/v1/*" }
        $hasLegacyAddress = $paths -contains "/detect/address"
        $hasLegacyBatch = $paths -contains "/batch/address"

        if ($hasApiV1) {
            $result.style = "api_v1_prefixed"
        } elseif ($hasLegacyAddress -or $hasLegacyBatch) {
            $result.style = "legacy_unprefixed"
        }
    } catch {
        $result.reachable = $false
    }

    try {
        $health = Invoke-RestMethod -Uri $result.healthUrl -TimeoutSec 4
        $result.healthBody = $health

        if ($result.style -eq "unknown") {
            if ($health.service -eq "eKYC Address Detector") {
                $result.style = "legacy_unprefixed"
            } elseif ($health.status -eq "ok") {
                $result.style = "api_v1_prefixed"
            }
        }
    } catch {
        # Health endpoint is optional for fingerprinting.
    }

    return $result
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Get-RepoRoot -StartPath $scriptDir

Push-Location $repoRoot
try {
    if (-not $SkipFetch) {
        git fetch origin --prune | Out-Null
    }

    $branch = git branch --show-current
    $commit = git rev-parse --short HEAD

    $inMain = Test-RemoteContains -Commit $commit -RemoteBranch "origin/main"
    $inBackend = Test-RemoteContains -Commit $commit -RemoteBranch "origin/backend"

    $api = Get-ApiFingerprint -Url $BaseUrl

    Write-Host "=== Backend Source Detection ==="
    Write-Host "Repo root: $repoRoot"
    Write-Host "Current branch: $branch"
    Write-Host "Current commit: $commit"
    Write-Host "Contained in origin/main: $inMain"
    Write-Host "Contained in origin/backend: $inBackend"
    Write-Host ""
    Write-Host "Server base URL: $BaseUrl"
    Write-Host "OpenAPI URL: $($api.openapiUrl)"
    Write-Host "Health URL: $($api.healthUrl)"
    Write-Host "Reachable: $($api.reachable)"
    Write-Host "Detected API style: $($api.style)"

    if ($api.foundPaths.Count -gt 0) {
        Write-Host ""
        Write-Host "Key route check:"
        Write-Host "- has /api/v1/* routes: $([bool]($api.foundPaths | Where-Object { $_ -like '/api/v1/*' }))"
        Write-Host "- has /detect/address: $($api.foundPaths -contains '/detect/address')"
        Write-Host "- has /batch/address: $($api.foundPaths -contains '/batch/address')"
    }

    if ($null -ne $api.healthBody) {
        Write-Host ""
        Write-Host "Health response snapshot:"
        $api.healthBody | ConvertTo-Json -Depth 6
    }

    Write-Host ""
    if (-not $api.reachable) {
        Write-Host "Result: Server not reachable. Branch/commit detection still valid for your local code checkout."
    } elseif ($api.style -eq "api_v1_prefixed") {
        Write-Host "Result: Running app matches API v1 prefixed style."
    } elseif ($api.style -eq "legacy_unprefixed") {
        Write-Host "Result: Running app matches legacy unprefixed style."
    } else {
        Write-Host "Result: Could not classify API style with high confidence."
    }
}
finally {
    Pop-Location
}
