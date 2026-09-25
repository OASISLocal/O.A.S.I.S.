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

## table

```liquid
{% raw %}{% capture rows %}
| Nivel | RAM | VRAM |
|---|---|---|
| Mínimo | 8 GB | — |
{% endcapture %}
{% include components/table.html body=rows caption="Requisitos" sortable="true"
   note="Estas son cifras declaradas, no benchmarks medidos." %}{% endraw %}
```

La tabla vive en un contenedor con scroll horizontal, así que en un móvil de
360 px se desliza en lugar de romper la página. `sortable="true"` añade
ordenación; la columna se detecta como numérica si el 80 % de sus celdas lo son.

## chart

El gráfico **se dibuja desde una tabla que está en el marcado**, no desde datos
en JavaScript. Por eso el dibujo y las cifras no pueden discrepar, y un motor de
respuestas lee la tabla.

```liquid
{% raw %}{% capture data %}
| Gemma 4B (Q4) | 4.1 |
| Llama 3.2 3B (Q4) | 2.0 |
{% endcapture %}
{% include components/chart.html body=data chart="bar" unit=" GB"
   title="Tamaño de descarga" sub="Cuantizado a Q4"
   note="Tamaños declarados. No es una prueba de velocidad." %}{% endraw %}
```

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

## Página de pruebas

`_posts/2026-09-25-every-component-on-one-page.md` ejercita todos los
componentes. Está marcada `noindex: true` y `sitemap: false`, y `check_site.py`
falla si un post así aparece en el sitemap, en un índice o en un feed.

## Añadir un componente

1. `_includes/components/nombre.html`.
2. `assets/components/nombre.css` y/o el bloque en `components.js`.
3. Su marcador `data-cmp-nombre` en el HTML del include.
4. Añadir el nombre a la detección en `_layouts/post.html`.
5. Ejercitarlo en la página de pruebas.

`check_seo.py` verifica que todo lo anterior siga en su sitio.
