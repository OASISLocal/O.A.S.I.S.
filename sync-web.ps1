<#
.SYNOPSIS
  Sync the OASIS website: checks, commit, push to origin + production (github-pages).
.DESCRIPTION
  1. Pre-push checks (old URLs, JSON validity, canonicals).
  2. Commits everything on main.
  3. Pushes to origin (staging) and production (OASISLocal/O.A.S.I.S. : github-pages).
  Run from anywhere: the script cds to its own folder.
.EXAMPLE
  .\sync-web.ps1
  .\sync-web.ps1 -Message "Hero: new announcement pill"
#>
param([string]$Message = "")

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

function Fail($msg) { Write-Host "SYNC ABORTED: $msg" -ForegroundColor Red; exit 1 }

# ---------- 1. Pre-push checks ----------
Write-Host "== checks ==" -ForegroundColor Cyan

$badOld = Select-String -Path *.html, *.xml, *.txt, _layouts/*.html, _posts/*.md, blog/*.html, blog/*.json -Pattern "OASISLocal/oasis[^.]|github\.io/OASIS[^.]" -ErrorAction SilentlyContinue |
  Where-Object { $_.Line -notmatch "O\.A\.S\.I\.S\." }
if ($badOld) { $badOld | ForEach-Object { Write-Host ("  " + $_.Filename + ":" + $_.LineNumber) }; Fail "old repo/paths URLs found above" }

try { Get-Content -Raw roadmap.json | ConvertFrom-Json | Out-Null } catch { Fail "roadmap.json is not valid JSON" }

$missingCanon = Get-ChildItem -Filter *.html | Where-Object {
  (Get-Content -Raw $_.FullName) -notmatch 'rel="canonical"'
} | Select-Object -ExpandProperty Name
if ($missingCanon) { Fail ("pages without canonical: " + ($missingCanon -join ", ")) }

Write-Host "checks OK" -ForegroundColor Green

# ---------- 2. Commit ----------
Write-Host "== commit ==" -ForegroundColor Cyan
git add -A
$pending = git status --porcelain
if (-not $pending) { Write-Host "nothing to commit, continuing to push" }
else {
  if (-not $Message) { $Message = "Web update " + (Get-Date -Format "yyyy-MM-dd HH:mm") }
  git commit -m $Message
  if ($LASTEXITCODE -ne 0) { Fail "git commit failed" }
}

# ---------- 3. Push origin (staging) ----------
Write-Host "== push origin/main ==" -ForegroundColor Cyan
git push origin main
if ($LASTEXITCODE -ne 0) { Fail "push to origin failed" }

# ---------- 4. Merge production + push github-pages ----------
Write-Host "== sync production/github-pages ==" -ForegroundColor Cyan
git fetch production github-pages
if ($LASTEXITCODE -ne 0) { Fail "fetch production failed (check PAT / access)" }
git merge --no-edit -X ours production/github-pages
if ($LASTEXITCODE -ne 0) { Fail "merge conflict: resolve manually, then re-run" }
git push production main:github-pages
if ($LASTEXITCODE -ne 0) { Fail "push to production failed" }

Write-Host ""
Write-Host "SYNC DONE: live in ~1-3 min at https://oasislocal.github.io/O.A.S.I.S./" -ForegroundColor Green
