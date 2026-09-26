param([string]$Only = '')
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$cache = @{}

function Get-Translation([string]$text) {
  $trimmed = $text.Trim()
  if ($trimmed -match '§\d+§') { return $text }
  if (-not $trimmed -or $trimmed -notmatch '[A-Za-z]') { return $text }
  if ($trimmed.Length -gt 4500 -or $trimmed -match '^[A-Z0-9_./%+:-]+$') { return $text }
  if ($cache.ContainsKey($trimmed)) { return $text.Replace($trimmed, $cache[$trimmed]) }
  $uri = 'https://api.mymemory.translated.net/get?q=' + [uri]::EscapeDataString($trimmed) + '&langpair=en|es'
  try {
    $data = Invoke-RestMethod -Uri $uri -TimeoutSec 30
    $translated = $data.responseData.translatedText
    if ($translated) { $cache[$trimmed] = $translated; Start-Sleep -Milliseconds 80; return $text.Replace($trimmed, $translated) }
  } catch { }
  return $text
}

function Translate-Block([string]$html) {
  $protected = @{}
  $index = 0
  $html = [regex]::Replace($html, '(?is)<(script|style|pre|code)(\b[^>]*)?>.*?</\1>', {
    param($m)
    $key = "§$($m.Index)§"
    $index++
    $protected[$key] = $m.Value
    $key
  })
  $html = [regex]::Replace($html, '(?s)>([^<>]+)<', {
    param($m)
    '>' + (Get-Translation $m.Groups[1].Value) + '<'
  })
  foreach ($key in $protected.Keys) { $html = $html.Replace($key, $protected[$key]) }
  $html = [regex]::Replace($html, '(?i)(<(?:title|meta|input|textarea|button|a|img)\b[^>]*?\s(?:content|placeholder|aria-label|alt|title)\s*=\s*["''])([^"'']+)(["''])', {
    param($m)
    $value = $m.Groups[2].Value
    if ($value -match '^(https?://|/|[A-Za-z0-9_.-]+\.(?:html|css|js|svg|ico|woff2))') { return $m.Value }
    $m.Groups[1].Value + (Get-Translation $value) + $m.Groups[3].Value
  })
  return $html
}

$pages = @{
  'index.html' = 'es.html'
  '404.html' = 'es/404.html'
  'about.html' = 'es/about.html'
  'changelog.html' = 'es/changelog.html'
  'comparison.html' = 'es/comparison.html'
  'download.html' = 'es/download.html'
  'eula.html' = 'es/eula.html'
  'faq.html' = 'es/faq.html'
  'features.html' = 'es/features.html'
  'how-it-works.html' = 'es/how-it-works.html'
  'models.html' = 'es/models.html'
  'pricing.html' = 'es/pricing.html'
  'privacy-policy.html' = 'es/privacy-policy.html'
  'privacy.html' = 'es/privacy.html'
  'requirements.html' = 'es/requirements.html'
  'security.html' = 'es/security.html'
  'third-party-notices.html' = 'es/third-party-notices.html'
  'tools.html' = 'es/tools.html'
}

# From _config.yml, via site_config.py. These three rewrites used to carry the
# subpath written out by hand, in three places, next to six copies of the domain.
$cfgScript = Join-Path $root 'site_config.py'
$basePath = (python $cfgScript BASEURL).Trim()
$siteUrl = (python $cfgScript SITE).Trim()
$pAssets = 'href="' + $basePath + 'assets/'
$sAssets = 'src="' + $basePath + 'assets/'
$pEsHome = 'href="' + $basePath + 'es/"'
$pSiteHome = 'href="' + $siteUrl + '/"'

foreach ($pair in $pages.GetEnumerator()) {
  if ($Only -and $pair.Key -ne $Only) { continue }
  try {
    $source = [IO.File]::ReadAllText((Join-Path $root $pair.Key))
    $translated = Translate-Block $source
    $translated = $translated.Replace('lang="en"', 'lang="es"').Replace('og:locale" content="en_US"', 'og:locale" content="es_ES"')
    $translated = $translated.Replace('hreflang="en"', 'hreflang="__ES__"').Replace('hreflang="es"', 'hreflang="en"').Replace('hreflang="__ES__"', 'hreflang="es"')
    $translated = $translated.Replace('href="assets/', $pAssets).Replace('src="assets/', $sAssets)
    $translated = $translated.Replace('href="index.html"', $pEsHome).Replace('href="/"', $pEsHome)
    $translated = $translated.Replace($pSiteHome, $pEsHome)
    $target = Join-Path $root $pair.Value
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($target)) | Out-Null
    [IO.File]::WriteAllText($target, $translated, [Text.UTF8Encoding]::new($false))
    Write-Host "translated $($pair.Key) -> $($pair.Value)"
  } catch { Write-Warning "failed $($pair.Key): $($_.Exception.Message)" }
}
