# Componentes del Journal

Sintaxis de cada componente. Cuando escribas un artículo, míralo aquí en vez de
inventar HTML: los componentes existen para que no haya que escribir HTML a mano.

> **Por qué no hay librerías.** El sitio promete cero rastreadores y cero
> peticiones a terceros (`METRICS.md`, el pie de cada página, `privacy.html`).
> Chart.js, Mermaid o GLightbox desde un CDN romperían esa promesa y añadirían un
> punto único de fallo. Todo aquí es **vanilla, autoalojado y sin dependencias**:
> los gráficos se dibujan en SVG con ~150 líneas propias, el lightbox son ~100.
>
> **Todo degrada.** Con el JavaScript bloqueado, los callouts, las tablas, los
> acordeones, las timelines y las pestañas siguen viéndose y funcionando,
> porque el marcado es HTML real. El script solo añade ordenación, lightbox,
> pestañas y el dibujo del gráfico.

## Índice

| Componente | Archivo | Carga |
|---|---|---|
| Callout | `_includes/components/callout.html` | `callout.css` |
| Acordeón / FAQ | `_includes/components/details.html` | `details.css` |
| Tabla | `_includes/components/table.html` | `table.css` |
| Gráfico | `_includes/components/chart.html` | `chart.css` |
| Timeline | `_includes/components/timeline.html` | `timeline.css` |
| Pestañas | `_includes/components/tabs.html` | `tabs.css` |
| Vídeo | `_includes/components/video.html` | `video.css` |
| Galería | `_includes/components/gallery.html` | `gallery.css` |
| Relacionados | automático en el layout | `related.css` |

`assets/components/base.css` se carga siempre que haya cualquier componente, y
`assets/components/components.js` es el único script.

## Cómo se llama un include

Jekyll no admite cuerpo de bloque en un `{% raw %}{% include %}{% endraw %}`, así que
el cuerpo se captura primero:

```liquid
{% raw %}{% capture texto %}
Markdown **normal** aquí, con [enlaces](/how-it-works.html).
{% endcapture %}
{% include components/callout.html type="note" body=texto %}{% endraw %}
```

Alternativa para una sola línea: el HTML puro sigue permitido en el `.md`.

## Carga condicional

`_layouts/post.html` detecta solo qué componentes usa el artículo buscando su
marcador `data-cmp-*` en el contenido renderizado. Un artículo de texto puro no
pide ni un CSS. Para forzarlo desde el front matter:

```yaml
components: "chart gallery"
```

Si añades un componente nuevo, addselo a la lista de detección del layout.

## callout

Tipos: `note` (por defecto) · `tip` · `warning` · `measured`.

```liquid
{% raw %}{% capture t %}Cuerpo en markdown.{% endcapture %}
{% include components/callout.html type="warning" body=t %}
{% include components/callout.html type="note" title="Un título" body=t %}{% endraw %}
```

`warning` es el único con color, y sigue llevando palabra: el significado nunca
depende del color. **`measured` existe para cifras de rendimiento** y se ve
deliberadamente distinto, para que nadie cite un número sin sus condiciones.

## details (acordeón / FAQ)

Sobre `<details>` nativo, así que funciona sin JavaScript.

```liquid
{% raw %}{% capture faq %}
- **¿Pregunta?**
  Respuesta.
- **¿Otra?**
  Respuesta.
{% endcapture %}
{% include components/details.html title="Preguntas" faq="true" body=faq %}{% endraw %}
```

`faq="true"` pone pregunta y respuesta en dos columnas en pantallas anchas.
`-open-label` / `-close-label` traducen los botones de expandir.

`open` decide cuántas preguntas arrancan desplegadas:

| valor | efecto |
|---|---|
| `all` (por defecto) | todas abiertas |
| `first` | solo la primera, que es la que suele haber traído a la gente |

En un artículo usa `open="first"`: con las cinco abiertas el FAQ es un muro de
texto. La página de pruebas deja el valor por defecto a propósito, para que
ambos comportamientos se vean probados.

`schema="faqpage"` emite además datos estructurados `FAQPage`, construidos con
las mismas cadenas que las respuestas visibles, así que no pueden divergir. Merece
la pena ser preciso sobre su valor: Google restringió los rich results de FAQ a
sitios autorizados de salud y gobierno, así que **aquí no va a generar un
snippet**. Sirve para motores de respuesta y herramientas que leen datos
estructurados. `check_seo.py` lo parsea y comprueba que las preguntas del schema
son las mismas que se ven en la página, porque un JSON inválido o desalineado no
deja ni una marca visible.

## table

La tabla se escribe como **HTML**, no como markdown, y **con la clase puesta**:

```liquid
{% raw %}{% capture rows %}
<table class="cmp-table">
  <thead>
    <tr><th scope="col">Tier</th><th scope="col" data-sort data-key="ram">RAM</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Minimum</th><td>8 GB</td></tr>
  </tbody>
</table>
{% endcapture %}
{% include components/table.html body=rows caption="Requisitos" sortable="true"
   note="Estas son cifras declaradas, no benchmarks medidos." %}{% endraw %}
```

**Por qué HTML y no markdown:** kramdown envuelve el contenido de bloque en
`<p>`, y un `<p>` dentro de un `<table>` es HTML inválido: rompe el build de
Jekyll. Por eso el cuerpo se pasa tal cual.

**Por qué la clase va en el `<table>` y no la pone el script:** las reglas de
disposición (celdas sin salto de línea, cabecera pegajosa) tienen que estar
activas *antes* de que corra JavaScript, y son las que mantienen una tabla
ancha dentro de su contenedor con scroll en un móvil. El script sólo rellena lo
que el autor olvidó.

La tabla vive en un contenedor con scroll horizontal, así que en un móvil se
desliza en lugar de romper la página. `sortable="true"` añade ordenación (marca
`data-sort` en las cabeceras); la columna se detecta como numérica si el 80 % de
sus celdas lo son. `-sort="ram"` ordena por la columna con ese `data-key`.

## chart

El gráfico **se dibuja desde una tabla que está en el marcado**, no desde datos
en JavaScript. Por eso el dibujo y las cifras no pueden discrepar, y un motor de
respuestas lee la tabla. El cuerpo es HTML por la misma razón que en `table`.

```liquid
{% raw %}{% capture data %}
<tbody>
  <tr><th scope="row">Gemma 4B (Q4)</th><td data-value="4.1">4.1</td></tr>
  <tr><th scope="row">Llama 3.2 3B (Q4)</th><td data-value="2.0">2.0</td></tr>
</tbody>
{% endcapture %}
{% include components/chart.html body=data chart="bar" unit=" GB"
   title="Tamaño de descarga" sub="Cuantizado a Q4"
   note="Tamaños declarados. No es una prueba de velocidad." %}{% endraw %}
```

Se pasa sólo el `<tbody>`: el `<table>` y sus cabeceras los pone el include.
`data-value` es el número que usa el dibujo; la celda muestra el mismo valor en
texto legible.

`chart="bar|line"`. El botón "Show the numbers" revela la tabla, que siempre está
en el DOM. **Pon siempre la nota**: un gráfico sin contexto es cómo se cita una
cifra sin sus condiciones.

## timeline

```liquid
{% raw %}{% capture tl %}
- **2026-09-20 · v0.2.0** — la versión Mono.
- **Planificado** — build de Linux.
{% endcapture %}
{% include components/timeline.html body=tl horizontal="true" %}{% endraw %}
```

Estados: `**Ahora**` (punto relleno) y `**Planificado**` (punteado, atenuado,
pero visible: lo que no ha salido se enseña, no se esconde).

## tabs

Patrón de pestañas WAI-ARIA: una sola parada de tabulación, flechas para mover.

```liquid
{% raw %}{% include components/tabs.html id="shell" labels="PowerShell|Bash"
   panels="```powershell
...
```
|```bash
...
```" %}{% endraw %}
```

## video

```liquid
{% raw %}{% include components/video.html id="VIDEO_ID" provider="youtube"
   title="Título" poster="/assets/posters/lo.png" caption="Pie" %}{% endraw %}
```

El iframe **no existe hasta que se hace clic**, así que un artículo con tres
vídeos no cuesta ninguna petición a terceros mientras se lee. El póster **debe
ser local**: una miniatura remota sería exactamente la petición de terceros que
el sitio no hace. Se usa `youtube-nocookie.com`.

## gallery

```liquid
{% raw %}{% include components/gallery.html title="Capturas" images="/a.png|Pie1|Alt1|/a-full.png, /b.png|Pie2|Alt2" %}{% endraw %}
```

Formato: `src|caption|alt|full-size-src`, separados por comas. El **alt es
obligatorio**: si falta queda vacío a propósito, para que un lector de pantalla
no lea un nombre de archivo. Lightbox con flechas y `Esc`, y devuelve el foco a la
miniatura.

## related

Automático: mismo `tags` primero, después cualquier otro, nunca el propio
artículo ni su traducción (mismo `ref`). Con menos de tres, el bloque
desaparece en vez de rellenarse con contenido débil.

## Peso de página: lo que sirve y lo que no

Medido con Lighthouse en móvil (3 ejecuciones, 14 páginas), no a ojo:

| Recurso | Peso real | Nota |
|---|---|---|
| CSS | 2,5-8 KB | Los 133 KB de `style.css` son el **tamaño en disco**; gzip lo baja a 4 KB |
| JS | 5-7,6 KB | |
| Fuentes | 74-102 KB | lo que de verdad pesa |
| Página | 76-316 KB | |

Total: 188-286 KB por página, rendimiento 0,96-0,99, CLS 0,000-0,021.

**Dos cosas que se intentaron y no valieron la pena.** Están aquí para que nadie
vuelva a perder el tiempo en ellas:

1. **Quitar los preloads de fuentes de las páginas de producto.** Ahorraba
   40-80 KB, pero provocation CLS de hasta 0,16 en cuatro páginas. Se debe a que
   esas páginas usan las fuentes a través de `var(--display)` y `var(--mono)`
   definidas en el CSS que enlazan, no por nombre: un escaneo del texto de la
   página no lo ve. Los preloads se quedaron.
2. **Suponer que las fuentes estaban sin recortar.** `build_fonts.py` las
   recorta a los 113 caracteres que el sitio dibuja de verdad y ahorra un 13%
   (130 → 114 KB), pero ese 13% es el techo real: ya venían subconjuntadas a
   latino. El "55% de glifos sin usar" que aparecia en las metricas era
   enganoso: contaba glifos que la fuente nunca tuvo.

Lo que sí queda por debajo del suelo: 74 KB de fuentes es el precio de la
tipografía de marca, y bajarlo significa usar menos de las cuatro familias, que
es una decisión de diseño y no de rendimiento.

## Las fuentes se recortan, y se comprueba

```
python build_fonts.py            # recorta assets/fonts/*.woff2
python build_fonts.py --check    # falla si no están recortadas (lo corre sync-web.ps1)
```

El recorte es la unión de los rangos latinos que puede contener el texto y de
**todos los caracteres que el sitio realmente dibuja**. La segunda mitad es la
importante: si el sitio dibuja ■ ✓ ≠ y el recorte los tira, aparece un cuadro
vacío que ninguna comprobación detecta. `--check` compara contra el `.orig` de
cada fuente y avisa si el recorte perdió un glifo que la original tenía.

## Los datos estructurados se generan, no se escriben

Todo el schema del sitio sale de algo que ya existe, para que no pueda separarse
de lo que el lector ve:

| Qué | Se genera de | Comprobación |
|---|---|---|
| `FAQPage` de los artículos | el propio componente `details` | `check_seo.py` parsea el JSON y compara las preguntas con los `<summary>` visibles |
| `FAQPage` de `/faq.html` | los `<details>` de esa misma página | `build_faqpage.py --check` |
| `DefinedTermSet` del glosario | `tooltips.json` + `tooltips.es.json` | `build_glossary.py --check` |
| `llms.txt` | `site-data.json` + los artículos publicados | `build_llms.py --check` |
| `sitemap.xml` | las rutas reales + fecha del último commit | `build_sitemap.py` |

La razón por la que son generadores y no ficheros a mano está en los fallos que
ya costaron tiempo: el FAQPage de `faq.html` preguntaba *"Does OASIS really work
offline?"* mientras la página decía *"Does it really work offline?"*, en otro
orden, y ninguna comprobación lo notó porque nadie comparaba las dos cosas.

Cuando añadas un `FAQPage` a una página nueva, Genéralo desde sus propias
preguntas visibles en lugar de escribir el JSON a mano.

## Poner un artículo en la ruta de lectura

El índice del Journal construye el orden de lectura solo, a partir del front
matter del artículo:

```yaml
tags: [basics]
series: foundations   # agrupa
order: 3              # secuencia dentro de la serie
```

No hay que tocar `blog/Index.html` ni `es/blog/index.html` al publicar: el
índice enumera las series, numera las partes y enlaza al gemelo en español
cuando existe. El índice en inglés muestra el `excerpt` del artículo; el español
prefiere el del gemelo y, si no hay, cae en `_data/blog_es.yml` y marca la
insignia `EN`.

## Página de pruebas

`_posts/2026-09-25-every-component-on-one-page.md` ejercita todos los
componentes. Está marcada `noindex: true` y `sitemap: false`, y `check_site.py`
falla si un post así aparece en el sitemap, en un índice o en un feed.

Verificarla bien necesita un navegador, no sólo el HTML:

```
# build real (imprescindible: kramdown y Liquid fallan aquí)
bundle exec jekyll build

# y después, con el build servido en el subpath correcto
python <script que sirva _site y lance headless Chrome>
```

El subpath importa: los assets del blog apuntan a `/O.A.S.I.S./assets/...`, así
que servir `_site` en la raíz hace que el CSS no cargue y parezca un fallo de
estilos que no existe.

## Verificar un componente que "no hace nada"

Tres fallos que ya ocurrieron aquí, para no repetirlos:

1. **Un `<template>` no expone su contenido por `textContent`.** El contenido
   vive en un `DocumentFragment` inerte; hay que leer `innerHTML`.
2. **`data-sort` puede escribirse sin valor** (`data-sort=""`). Hay que
   seleccionar por presencia del atributo, no por su valor.
3. **La clase del `<table>` va en el marcado, no la pone el script.** Las reglas
   de disposición tienen que estar activas antes de que corra JavaScript.

`check_seo.py` comprueba ahora que cada include emite el marcador que el
script busca, y viceversa, así que un componente que se renderiza pero nunca se
inicializa falla antes de desplegar.

## Añadir un componente

1. `_includes/components/nombre.html`.
2. `assets/components/nombre.css` y/o el bloque en `components.js`.
3. Su marcador `data-cmp-nombre` en el HTML del include.
4. Añadir el nombre a la detección en `_layouts/post.html`.
5. Ejercitarlo en la página de pruebas.

`check_seo.py` verifica que todo lo anterior siga en su sitio.
