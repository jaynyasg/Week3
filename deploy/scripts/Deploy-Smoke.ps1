<#
.SYNOPSIS
  Smoke-test a deployed AgentForge instance (health, ready, auth, optional campaign).

.PARAMETER BaseUrl
  Public base URL, e.g. https://agentforge-security.onrender.com

.PARAMETER OperatorToken
  Bearer token for operator routes. If omitted, uses environment variable AGENTFORGE_OPERATOR_TOKEN.

.EXAMPLE
  .\deploy\scripts\Deploy-Smoke.ps1 -BaseUrl "https://agentforge-security.onrender.com"

.EXAMPLE
  $env:AGENTFORGE_OPERATOR_TOKEN = "..."
  .\deploy\scripts\Deploy-Smoke.ps1 -BaseUrl "https://agentforge-security.onrender.com" -Campaign
#>
param(
    [Parameter(Mandatory = $true)]
    [string] $BaseUrl,

    [string] $OperatorToken = $env:AGENTFORGE_OPERATOR_TOKEN,

    [switch] $Campaign
)

$ErrorActionPreference = "Stop"
$base = $BaseUrl.TrimEnd("/")

function Invoke-JsonGet([string] $path) {
    $u = "$base$path"
    Write-Host "GET $u"
    $r = curl.exe -sS --max-time 30 "$u"
    if ($LASTEXITCODE -ne 0) { throw "curl failed: $u" }
    return $r
}

Write-Host "=== /health ==="
$h = Invoke-JsonGet "/health" | ConvertFrom-Json
if ($h.status -ne "ok") { throw "/health unexpected: $($h | ConvertTo-Json -Compress)" }
Write-Host "OK: health"

Write-Host "=== /ready ==="
$ready = Invoke-JsonGet "/ready" | ConvertFrom-Json
Write-Host ($ready | ConvertTo-Json -Compress)
if ($ready.status -ne "ready") { Write-Warning "status is not 'ready' (target or operator may be unset)" }
if ($ready.evidence_environment -ne "deployed") { Write-Warning "evidence_environment is not 'deployed'" }

Write-Host "=== /operator/status unauthenticated (expect 401) ==="
$u401 = "$base/operator/status"
$code = curl.exe -sS -o NUL -w "%{http_code}" --max-time 30 "$u401"
if ($code -ne "401") { throw "Expected 401 without token, got HTTP $code" }
Write-Host "OK: 401 without auth"

if (-not [string]::IsNullOrEmpty($OperatorToken)) {
    Write-Host "=== /operator/status authenticated ==="
    $authHdr = "Authorization: Bearer $OperatorToken"
    $body = curl.exe -sS --max-time 30 -H $authHdr "$u401"
    if ($LASTEXITCODE -ne 0) { throw "curl failed (authenticated status)" }
    $st = $body | ConvertFrom-Json
    Write-Host ($st | ConvertTo-Json -Compress)
    Write-Host "OK: authenticated status"
}
else {
    Write-Warning "No operator token: set AGENTFORGE_OPERATOR_TOKEN or pass -OperatorToken for authenticated checks."
}

if ($Campaign) {
    if ([string]::IsNullOrEmpty($OperatorToken)) { throw "-Campaign requires operator token" }
    $tmp = New-TemporaryFile
    Set-Content -Path $tmp -Encoding utf8 -Value '{"case_ids":["rbac-nurse-labs-001"],"max_cases":1,"budget_usd":0.10}'
    Write-Host "=== POST /operator/campaigns (bounded) ==="
    $camp = curl.exe -sS --max-time 120 -X POST "$base/operator/campaigns" `
        -H "Authorization: Bearer $OperatorToken" `
        -H "Content-Type: application/json" `
        --data-binary "@$tmp"
    Remove-Item $tmp -Force
    if ($LASTEXITCODE -ne 0) { throw "campaign curl failed" }
    $run = $camp | ConvertFrom-Json
    $ex = $run.exchanges
    if (-not $ex -or $ex.Count -lt 1) {
        throw "Campaign returned no exchanges. Check Render disk mount vs AGENTFORGE_ARTIFACT_DIR and evals/cases in image."
    }
    Write-Host "OK: campaign run_id=$($run.run_id) exchanges=$($ex.Count)"
}

Write-Host "Smoke finished."
