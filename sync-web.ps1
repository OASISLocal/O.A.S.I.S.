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

# Build the search path list, skipping folders that no longer exist (the
# Journal starts empty, so _posts/ can be absent).
$searchPaths = @()
foreach ($p in @("*.html", "*.xml", "*.txt", "launch/*.html", "_layouts/*.html", "_posts/*.md", "blog/*.html", "blog/*.json")) {
  if (Get-ChildItem -Path $p -ErrorAction SilentlyContinue) { $searchPaths += $p }
}
$badOld = Select-String -Path $searchPaths -Pattern "OASISLocal/oasis[^.]|github\.io/OASIS[^.]" -ErrorAction SilentlyContinue |
  Where-Object { $_.Line -notmatch "O\.A\.S\.I\.S\." }
if ($badOld) { $badOld | ForEach-Object { Write-Host ("  " + $_.Filename + ":" + $_.LineNumber) }; Fail "old repo/paths URLs found above" }

try { [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot "site-data.json")) | ConvertFrom-Json | Out-Null } catch { Fail "site-data.json is not valid JSON" }
try { [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot "launch.json")) | ConvertFrom-Json | Out-Null } catch { Fail "launch.json is not valid JSON" }

# Canonical is mandatory on plain static pages. Files with Jekyll front matter get
# their head from _layouts at build time, so they are checked by check_seo.py
# against the layout instead of here.
$missingCanon = Get-ChildItem -Filter *.html | Where-Object {
  $html = Get-Content -Raw $_.FullName
  -not $html.TrimStart().StartsWith("---") -and $html -notmatch 'rel="canonical"'
} | Select-Object -ExpandProperty Name
if ($missingCanon) { Fail ("pages without canonical: " + ($missingCanon -join ", ")) }

$requiredSpanish = @(
  "es/index.html", "es/about.html", "es/changelog.html", "es/comparison.html",
  "es/download.html", "es/eula.html", "es/faq.html", "es/features.html",
  "es/how-it-works.html", "es/models.html", "es/pricing.html", "es/privacy.html",
  "es/privacy-policy.html", "es/requirements.html", "es/security.html",
  "es/third-party-notices.html", "es/tools.html", "tooltips.es.json",
  "assets/lang.js", "assets/lang.css"
)
$missingSpanish = $requiredSpanish | Where-Object { -not (Test-Path -LiteralPath $_) }
if ($missingSpanish) { Fail ("missing Spanish pages: " + ($missingSpanish -join ", ")) }

try { [xml](Get-Content -Raw sitemap.xml) | Out-Null } catch { Fail "sitemap.xml is not valid XML" }

# Social preview image must be a real PNG (social platforms reject SVG).
if (-not (Test-Path -LiteralPath "assets/og-card.png")) { Fail "missing assets/og-card.png (social preview image)" }

# The SEO / links / claims gate lives in Python so there is a single source of
# truth: check_site.py covers canonical, og/twitter, hreflang, JSON-LD, internal
# links, sitemap<->files and post pairing; check_claims.py covers the forbidden
# phrasings and unmeasured performance figures.
if (Get-Command python -ErrorAction SilentlyContinue) {
  Write-Host "-- python check_site.py" -ForegroundColor DarkGray
  python check_site.py
  if ($LASTEXITCODE -ne 0) { Fail "check_site.py failed (broken links, sitemap out of date, or a post without its ES twin)" }
  Write-Host "-- python check_claims.py" -ForegroundColor DarkGray
  python check_claims.py
  if ($LASTEXITCODE -ne 0) { Fail "check_claims.py failed (forbidden phrasing or an unmeasured performance figure)" }
  Write-Host "-- python check_seo.py" -ForegroundColor DarkGray
  python check_seo.py
  if ($LASTEXITCODE -ne 0) { Fail "check_seo.py failed (head tags, JSON-LD, hreflang reciprocity, robots.txt, unique titles, or an internal file that would be published)" }
} else {
  Write-Host "WARNING: python not found, skipping check_site.py / check_claims.py / check_seo.py" -ForegroundColor Yellow
}

if ($Mode -ne "live") {
  foreach ($f in @("launch/teaser.html", "launch/countdown.html")) {
    if (-not (Test-Path $f)) { Fail "missing $f" }
  }
}

Write-Host "checks OK" -ForegroundColor Green

# ---------- 2. Commit sources ----------
Write-Host "== commit ==" -ForegroundColor Cyan

# Regenerate sitemap.xml from the files before staging it, so a new post can
# never be published without its sitemap entries. check_site.py above already
# verified the current file matches; this brings it up to date.
if (Get-Command python -ErrorAction SilentlyContinue) {
  Write-Host "-- regenerating sitemap.xml" -ForegroundColor DarkGray
  python build_sitemap.py
  if ($LASTEXITCODE -ne 0) { Fail "build_sitemap.py failed" }
  # The Google News sitemap stays dormant (ACTIVATED = False, and robots.txt does
  # not point at it), but the file is kept fresh so it is ready the day the
  # Publisher Center verification exists. See GOOGLE_NEWS.md.
  Write-Host "-- regenerating news-sitemap.xml (dormant)" -ForegroundColor DarkGray
  python build_news_sitemap.py
  if ($LASTEXITCODE -ne 0) { Fail "build_news_sitemap.py failed" }
}

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

  # A 404 raises, so the StatusCode check never ran and a dead site was still
  # reported as SYNC DONE. Read the real status, insist on our own content
  # rather than any 200, and retry while Pages rebuilds.
  function Get-PagesStatus($url) {
    try {
      $r = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 20
      return @{ code = [int]$r.StatusCode; body = $r.Content }
    } catch [System.Net.WebException] {
      $resp = $_.Exception.Response
      if ($resp) { return @{ code = [int]$resp.StatusCode; body = "" } }
      return @{ code = 0; body = "" }
    } catch {
      return @{ code = 0; body = "" }
    }
  }

  $marker = "O.A.S.I.S."
  $ok = $false
  $lastCode = 0
  foreach ($attempt in 1..8) {
    $res = Get-PagesStatus $siteUrl
    $lastCode = $res.code
    $hasContent = $res.body -and $res.body.Contains($marker)
    if ($res.code -eq 200 -and $hasContent) {
      $ok = $true
      Write-Host "Pages check OK: HTTP 200 with site content (intento $attempt/8)" -ForegroundColor Green
      break
    }
    Write-Host "  Pages aun no sirve el sitio: HTTP $($res.code), contenido=$hasContent (intento $attempt/8)" -ForegroundColor DarkGray
    if ($attempt -lt 8) { Start-Sleep -Seconds 20 }
  }

  if ($ok) {
    Write-Host "SYNC DONE: full site live at $siteUrl" -ForegroundColor Green
  } else {
    Write-Host "FALLO: $siteUrl responde HTTP $lastCode tras 8 intentos. El commit se subio, pero Pages NO esta publicando." -ForegroundColor Red
    Write-Host "  Comprueba en el repo de produccion: Settings > Pages > Source, y el ultimo run del workflow 'Deploy Jekyll with GitHub Pages'." -ForegroundColor Yellow
    Write-Host "  Sitemap, canonical y robots siguen apuntando a $siteUrl, asi que no hay alternativa hasta arreglarlo." -ForegroundColor Yellow
    exit 1
  }
} else {
  Write-Host "SYNC DONE: $Mode shell live in ~1-3 min. Full site NOT deployed (not even in view-source)." -ForegroundColor Green
  Write-Host "To go live later: set launch.json mode to live (or run with -Mode live) and re-run." -ForegroundColor Yellow
}
