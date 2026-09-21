$root = $PSScriptRoot
$base = 'https://oasislocal.github.io/O.A.S.I.S.'
$files = Get-ChildItem (Join-Path $root 'es') -Filter *.html
$files += Get-Item (Join-Path $root 'es.html')
foreach ($file in $files) {
  $name = if ($file.Name -eq 'es.html') { '' } else { $file.Name }
  $enUrl = if ($name) { "$base/$name" } else { "$base/" }
  $esUrl = if ($name) { "$base/es/$name" } else { "$base/es/" }
  $html = [IO.File]::ReadAllText($file.FullName)
  $html = [regex]::Replace($html, '<link rel="canonical" href="[^"]+">', '<link rel="canonical" href="' + $esUrl + '">')
  $nl = [Environment]::NewLine
  $alts = '<link rel="alternate" hreflang="es" href="' + $esUrl + '">' + $nl + '<link rel="alternate" hreflang="en" href="' + $enUrl + '">' + $nl + '<link rel="alternate" hreflang="x-default" href="' + $enUrl + '">'
  $html = [regex]::Replace($html, '(?m)<link rel="alternate" hreflang="[^"]+" href="[^"]+">', $alts)
  $html = [regex]::Replace($html, '(<meta property="og:url" content=")[^"]+(">)', '$1' + $esUrl + '$2')
  $html = $html.Replace('name="viewport" content="ancho = ancho del dispositivo, escala inicial = 1.0, ajuste de ventana grÃ¡fica = cubierta"', 'name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover"')
  $html = $html.Replace('name="robots" content="indexar, seguir"', 'name="robots" content="index, follow"')
  $html = [regex]::Replace($html, 'href="[^"]*" lang="es" hreflang="en">ES</a>', 'href="' + $enUrl + '" lang="en" hreflang="en">EN</a>')
  $html = $html.Replace('"url":"' + $base + '/"', '"url":"' + $esUrl + '"')
  [IO.File]::WriteAllText($file.FullName, $html, [Text.UTF8Encoding]::new($false))
}
