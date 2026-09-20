<#
.SYNOPSIS
  Sync the OASIS website: checks, commit, push to origin + deploy to production.
.DESCRIPTION
  Reads launch.json for the deployment phase:
    live      -> deploys the full site (current main tree).
    teaser    -> deploys ONLY launch/teaser.html as index.html. Nothing else.
    countdown -> deploys ONLY launch/countdown.html as index.html (date baked in).
  Non-live deploys contain just index.html + a minimal 404 + robots (disallow all).
  No sitemap, no blog, no full site anywhere — not even in view-source.
  Deploy is a snapshot commit on production/github-pages via a temp worktree,
  so history stays linear and merges never conflict.
.EXAMPLE
  .\sync-web.ps1
  .\sync-web.ps1 -Message "Hero: new announcement pill"
  .\sync-web.ps1 -Mode countdown -RevealDate "2026-12-01T12:00:00Z"
#>
param(
  [string]$Message = "",
  [ValidateSet("", "live", "teaser", "countdown")][string]$Mode = "",
  [string]$RevealDate = ""
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

function Fail($msg) { Write-Host "SYNC ABORTED: $msg" -ForegroundColor Red; exit 1 }

# ---------- 0. Resolve phase ----------
$launch = Get-Content -Raw launch.json | ConvertFrom-Json
if (-not $Mode) { $Mode = $launch.mode }
if (-not $Mode) { $Mode = "live" }
if ($Mode -eq "countdown" -and -not $RevealDate) { $RevealDate = $launch.revealDate }
if ($Mode -eq "countdown" -and -not $RevealDate) { Fail "countdown needs -RevealDate ISO-8601 or launch.json revealDate" }
Write-Host "== phase: $Mode ==" -ForegroundColor Cyan

# ---------- 1. Pre-push checks (full tree, always) ----------
Write-Host "== checks ==" -ForegroundColor Cyan

$badOld = Select-String -Path *.html, *.xml, *.txt, launch/*.html, _layouts/*.html, _posts/*.md, blog/*.html, blog/*.json -Pattern "OASISLocal/oasis[^.]|github\.io/OASIS[^.]" -ErrorAction SilentlyContinue |
  Where-Object { $_.Line -notmatch "O\.A\.S\.I\.S\." }
if ($badOld) { $badOld | ForEach-Object { Write-Host ("  " + $_.Filename + ":" + $_.LineNumber) }; Fail "old repo/paths URLs found above" }

try { [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot "site-data.json")) | ConvertFrom-Json | Out-Null } catch { Fail "site-data.json is not valid JSON" }
try { [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot "launch.json")) | ConvertFrom-Json | Out-Null } catch { Fail "launch.json is not valid JSON" }

$missingCanon = Get-ChildItem -Filter *.html | Where-Object {
  (Get-Content -Raw $_.FullName) -notmatch 'rel="canonical"'
} | Select-Object -ExpandProperty Name
if ($missingCanon) { Fail ("pages without canonical: " + ($missingCanon -join ", ")) }

$requiredSpanish = @("es/index.html", "es/download.html", "es/pricing.html", "es/privacy.html", "es/security.html", "es/faq.html", "es/blog/index.html")
$missingSpanish = $requiredSpanish | Where-Object { -not (Test-Path -LiteralPath $_) }
if ($missingSpanish) { Fail ("missing Spanish pages: " + ($missingSpanish -join ", ")) }

try { [xml](Get-Content -Raw sitemap.xml) | Out-Null } catch { Fail "sitemap.xml is not valid XML" }

if ($Mode -ne "live") {
  foreach ($f in @("launch/teaser.html", "launch/countdown.html")) {
    if (-not (Test-Path $f)) { Fail "missing $f" }
  }
}

Write-Host "checks OK" -ForegroundColor Green

# ---------- 2. Commit sources ----------
Write-Host "== commit ==" -ForegroundColor Cyan
git add -A
$pending = git status --porcelain
if (-not $pending) { Write-Host "nothing to commit, continuing" }
else {
  if (-not $Message) { $Message = "Web update " + (Get-Date -Format "yyyy-MM-dd HH:mm") + " [$Mode]" }
  git commit -m $Message
  if ($LASTEXITCODE -ne 0) { Fail "git commit failed" }
}

# ---------- 3. Push origin (staging, full sources always) ----------
Write-Host "== push origin/main ==" -ForegroundColor Cyan
git push origin main
if ($LASTEXITCODE -ne 0) { Fail "push to origin failed" }

# ---------- 4. Deploy snapshot to production ----------
Write-Host "== deploy $Mode to production/github-pages ==" -ForegroundColor Cyan
git fetch production github-pages
if ($LASTEXITCODE -ne 0) { Fail "fetch production failed (check access)" }

$wt = Join-Path ([System.IO.Path]::GetTempPath()) "oasis-deploy-wt"
if (Test-Path $wt) { git worktree remove --force $wt 2>$null; Remove-Item -LiteralPath $wt -Recurse -Force -ErrorAction SilentlyContinue }
git worktree prune
git worktree add --detach $wt production/github-pages
if ($LASTEXITCODE -ne 0) { Fail "worktree setup failed" }
try {
  Push-Location -LiteralPath $wt
  # Empty the tree (keep .git), then lay out exactly what this phase serves.
  git rm -r -q . ; if ($LASTEXITCODE -ne 0) { Fail "tree clear failed" }
  if ($Mode -eq "live") {
    git checkout main -- .
    if ($LASTEXITCODE -ne 0) { Fail "tree restore from main failed" }
  } else {
    $shell = if ($Mode -eq "teaser") { "launch/teaser.html" } else { "launch/countdown.html" }
    $html = [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot $shell))
    if ($Mode -eq "countdown") {
      try { [void][DateTime]$RevealDate } catch { Fail "RevealDate is not valid ISO-8601: $RevealDate" }
      $dt = [DateTime]$RevealDate
      $human = $dt.ToUniversalTime().ToString("dddd, dd MMMM yyyy HH:mm 'UTC'", [System.Globalization.CultureInfo]::InvariantCulture)
      $html = $html.Replace("__REVEAL_ISO__", $RevealDate).Replace("__REVEAL_HUMAN__", $human)
    }
    [System.IO.File]::WriteAllText((Join-Path $wt "index.html"), $html)
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "launch/404.html") -Destination (Join-Path $wt "404.html")
    [System.IO.File]::WriteAllText((Join-Path $wt "robots.txt"), "User-agent: *`nDisallow: /`n")
    New-Item -ItemType File -Path (Join-Path $wt ".nojekyll") -Force | Out-Null
    git add -A
  }
  $stamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd HH:mm')
  git commit -m "Deploy: $Mode ($stamp UTC)"
  if ($LASTEXITCODE -ne 0) { Fail "deploy commit failed" }
git push production HEAD:github-pages
  if ($LASTEXITCODE -ne 0) { Fail "push to production failed" }
} finally {
  Pop-Location
  git worktree remove --force $wt
}

Write-Host ""
if ($Mode -eq "live") {
  $siteUrl = "https://oasislocal.github.io/O.A.S.I.S./"
  try {
    $probe = Invoke-WebRequest -UseBasicParsing -Uri $siteUrl -TimeoutSec 20
    if ($probe.StatusCode -ne 200) { Write-Host "WARNING: Pages returned HTTP $($probe.StatusCode): $siteUrl" -ForegroundColor Yellow }
    else { Write-Host "Pages check OK: HTTP 200" -ForegroundColor Green }
  } catch {
    Write-Host "WARNING: Pages endpoint is unavailable or not configured: $siteUrl" -ForegroundColor Yellow
  }
  Write-Host "SYNC DONE: full site live in ~1-3 min at https://oasislocal.github.io/O.A.S.I.S./" -ForegroundColor Green
} else {
  Write-Host "SYNC DONE: $Mode shell live in ~1-3 min. Full site NOT deployed (not even in view-source)." -ForegroundColor Green
  Write-Host "To go live later: set launch.json mode to live (or run with -Mode live) and re-run." -ForegroundColor Yellow
}
