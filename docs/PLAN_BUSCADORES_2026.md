# Plan: searchedores al máximo para `oasisweb`

> Documento de trabajo. Marca el camino para que Google, los buscadores de IA,
> Bing y los índices independientes extraigan de la web todo lo que pueden dar,
> **sin romper las tres promesas del sitio**: sin trackers, sin afirmaciones
> inventadas, sin cambiar URLs existentes.

Fecha: 2026-09-25 · Ámbito: `oasisweb/` (sitio estático Jekyll + HTML plano,
publicado en `oasislocal.github.io/O.A.S.I.S.`).

Decisiones ya tomadas (no volver a preguntar):

| Decisión | Valor | Consecuencia |
|---|---|---|
| Dominio | Se queda en `github.io` hasta conseguir dominio real | IndexNow, GSC *domain property* y llaves por host quedan **bloqueados** (Fase 9) |
| Buscador interno en la web | **No** | Fuera de alcance. Nadie debe proponer Google CSE después (§8) |
| Motores | Google + IA/LLM + Bing/IndexNow/Yandex/Seznam/Naver + Mojeek/Marginalia/Yep | Todo el plan |

---

## 1. Diagnóstico: qué hay y qué falta

Verificado sobre el árbol actual. `!` = defecto real, noomitempty opinión.

### 1.1 Indexación y rastreo

| # | Hallazgo | Dónde | Efecto |
|---|---|---|---|
| !1 | `sitemap.xml` tiene 21 `<url>`. **Ninguna de las 17 páginas `/es/*` indexables aparece como `<loc>` propio**, sólo como `xhtml:link hreflang`. | `build_sitemap.py:121-128` | Los espejos ES sólo se descubren por hreflang. Google recomienda declarar ambas variantes en el sitemap |
| !2 | Todos los `lastmod` son la constante `"2026-09-21"` | `build_sitemap.py:21-40` | `lastmod` falso → Google lo descarta y recalcula el ritmo de rastreo |
| !3 | `changefreq` y `priority` fijos a mano | `build_sitemap.py:21-40` | Google los ignora por completo; sólo tienen efecto en otros motores |
| !4 | `404.html` sirve 200 visual pero sin `noindex`; `eula.html`, `privacy-policy.html`, `third-party-notices.html` sin JSON-LD | `404.html`, `eula.html`… | Ruido de rastreo, sin datos estructurados |
| !5 | `/privacy.html` y `/privacy-policy.html` coexisten, ambas indexables y ambas en el sitemap | `sitemap.xml` | Canibalización: dos URLs para el mismo contenido |
| !6 | `llms.txt` existe (34 líneas) y **nadie lo enlaza**; `robots.txt` no lo menciona | grep vacío en todo el HTML | Los rastreadores lo encuentran por URL, pero no hay señal de que sea para humanos ni de que esté vivo |
| !7 | `news-sitemap.xml` está vacío (50 B) y sin referenciar; `build_news_sitemap.py` tiene `ACTIVATED = False` y `sync-web.ps1:104-108` no lo regenera | `GOOGLE_NEWS.md` | Todo Google News construido y dormido |
| !8 | `docs/` **no** está en el `exclude` de Jekyll → el spec de hardening interno se publica en la web. Igual `readme` | `_config.yml:38-60` | Fuga de documentación interna |

### 1.2 Verificación con Google

| # | Hallazgo | Dónde |
|---|---|---|
| !9 | No hay `google-site-verification` en ninguna página | grep vacío en `*.html` |
| !10 | **En un subpath de `github.io` no se puede verificar con fichero**: Google exige el fichero en la **raíz del host** (`oasislocal.github.io/google<token>.html`), que no controlamos. Tampoco se puede añadir un TXT de DNS: no somos dueños de `github.io`. **La única vía hoy es el meta tag**, y hay que insertarlo en las ~40 páginas. | — |
| 11 | Bing Webmaster Tools **sí** se puede verificar hoy: importando la propiedad desde Search Console. Cero cambios en el HTML. | — |

### 1.3 Datos estructurados

| # | Hallazgo | Dónde |
|---|---|---|
| !12 | `index.html` tiene **dos** bloques `ld+json` separados (líneas 34-46 y 487): `SoftwareApplication` por un lado, `WebSite` + `Organization` por otro. Grafo fragmentado, sin `@id` cruzados | `index.html:34-46`, `index.html:487` |
| !13 | `SoftwareApplication` sólo declara `name` y `offers`. Faltan `softwareVersion` (0.2.0, ya está en `site-data.json:1-5`), `applicationCategory`, `operatingSystem`, `downloadUrl`/`installUrl`, `isAccessibleForFree`, `license`, `author`, `releaseNotes`, `featureList`, `screenshot`, `softwareRequirements` | `index.html:34-46` |
| !14 | El rich result de Software App **exige `aggregateRating` o `review`**. `PRODUCT_TRUTH.md` + `check_claims.py` prohíben inventar reseñas ni métricas ⇒ **ese rich result no es alcanzable** hoy. No prometerlo. Cuando haya reseñas orgánicas reales, se marcan | — |
| !15 | `Organization` de la home **no tiene `sameAs`**. El único `sameAs` del sitio está en `about.html:41-43`, apunta sólo a GitHub y declara `"name":"OASIS"` (no `O.A.S.I.S.`) | `index.html:487`, `about.html:41-43` |
| !16 | `pricing.html` no declara `Product`/`Offer` (sólo `download.html` tiene `Offer`) | grep por `@type` |
| !17 | `faq.html` declara `FAQPage` → **los FAQ rich results se apagaron globalmente el 7-may-2026**. El marcado se conserva sólo por legibilidad de IA, no por rich result. Invertir más effort ahí es tirar dinero | `faq.html` |
| !18 | **Cero etiquetas `<img>` en todo el sitio** (contado sobre `*.html` + `es/*.html`). Un único `og-card.png` para 40+ páginas | todo el árbol |
| 19 | `BlogPosting` existe y es correcto | `_layouts/default.html:82-95` |
| 20 | Falta `SiteNavigationElement` y falta `DefinedTermSet` para el glosario | `_data/journal_terms.json`, `tooltips.json` |
| !21 | **`check_site.py` no valida JSON-LD, ni og/twitter, ni reciprocidad de hreflang, ni `robots.txt`, ni unicidad de title/description** — pero el comentario de `sync-web.ps1:75-78` afirma que sí lo hace. O se añaden los checks o se corrige el comentario | `check_site.py`, `sync-web.ps1:75-78` |

### 1.4 IA / AEO / GEO

| # | Hallazgo |
|---|---|
| !22 | `robots.txt` no declara política de rastreadores de IA. Hoy, por defecto, todos están permitidos — pero por omisión, no por decisión |
| 23 | No hay bloques "answer-first" (definiciones de 2-3 líneas, tablas comparativas, fecha de modificación real, autoría identificable). Es el formato que las respuestas de IA copian y citan |
| !24 | `about.html` declara `Organization`, no `Person`. No hay autoría por artículo |
| !25 | Cero vídeo ⇒ nada para el paquete de vídeo. `VideoObject` sólo si algún día hay vídeo real |

### 1.5 Contenido y autoridad

| # | Hallazgo |
|---|---|
| !26 | El Journal tiene **2 artículos**. No hay materia prima que citar |
| !27 | `tools.html` guarda el inventario de ~100+ herramientas en **tablas HTML escritas a mano**. No existe `_data/tools.yml` ⇒ es imposible generar páginas, sitemap o índice por herramienta |
| 28 | `models.html` y `requirements.html` son candidatos naturales a páginas por modelo y por nivel de VRAM/RAM |
| 29 | `comparison.html` es la semilla de un patrón `/compare/<alternativa>` |

### 1.6 Rendimiento

| # | Hallazgo | Dónde |
|---|---|---|
| !30 | Lighthouse CI corre **sólo preset desktop** y `performance` en `warn`. Google indexa **mobile-first** y las páginas ES ni siquiera están en la lista de URLs | `.lighthouserc.json:5-35` |
| !31 | `numberOfRuns: 1` ⇒ ruido alto en las aserciones | `.lighthouserc.json:21` |
| 32 | Se preloadean 2 de 6 woff2. El resto bloquea el render. Falta medir `font-display` | `index.html:47-48`, `assets/fonts/fonts.css` |

### 1.7 Medición

| # | Hallazgo |
|---|---|
| 33 | `METRICS.md:11-16` prohíbe trackers. La Search Console API (datos agregados, cero JavaScript para el visitante) es la única forma de tener métricas reales manteniendo la promesa |

---

## 2. Lo que Google **no** va a dar (escribirlo evita semanas perdidas)

| Capacidad | Estado real | Consecuencia |
|---|---|---|
| Custom Search JSON API | **Cerrada a nuevos clientes**; los existentes caducan el **1-ene-2027** | No construir nada aquí. El buscador interno ya está descartado |
| FAQ rich results | Apagados el 7-may-2026 en todo Google Search | `FAQPage` se queda como estructura para IA, no como rich result |
| HowTo rich results | Retirados | No escribir markup HowTo |
| Sitelinks Searchbox / `potentialAction` | Retirados | No añadir |
| `speakable` | Retirado | No añadir |
| Indexing API de Google | Sólo para `JobPosting` y `BroadcastEvent` | **No aplicable.** No perder tiempo |
| IndexNow | Google no participa | Cubre Bing, Yandex, Seznam, Naver, Yep. Y el índice de Bing alimenta Copilot y parte de DuckDuckGo |
| Paquete local / Google Business Profile | Requiere dirección física | No aplica |
| AI Overviews / AI Mode | No hay interruptor ni esquema que lo active | Se gana con contenido verificable, estructura y CWV |
| Rich result de Software App | Exige `aggregateRating` o `review` | Bloqueado por `PRODUCT_TRUTH.md` hasta que haya reseñas reales |

---

## 3. Fases

Esfuerzo: S < ½ jornada · M ~1-2 jornadas · L >3 jornadas.
Cada fase termina con `python check_site.py` + `python check_claims.py` en verde.

### Fase 0 — Sellar las fugas (S)

Sin esto, cualquier trabajo posterior seuilda sobre cimientos que gotean.

1. `build_sitemap.py`: emitir **cada** ES gemelo como `<url>` propio con `hreflang`
   recíproco (EN⇄ES, `x-default`→EN). Pasa de 21 a ~38 URLs.
2. `build_sitemap.py`: derivar `lastmod` del último commit que toca cada fichero
   (`git log -1 --format=%as -- <path>`), con el valor actual como fallback.
   Eliminar `changefreq`/`priority` de la tabla manual y documentar que sólo
   informational para motores no-Google.
3. Resolver el canibalismo legal: elegir `privacy.html` como canónica y convertir
   `privacy-policy.html` en redirect, o al revés. Añadir el mecanismo de
   redirect que GitHub Pages soporte (hoja estática o `_redirects`, según lo que
   acepte el despliegue) + test en `check_site.py`.
4. `noindex` en `404.html`, `es/404.html`, `launch/*.html`.
5. `_config.yml`: añadir `docs/`, `readme`, `PLAN_BUSCADORES_2026.md` y cualquier
   nuevo `.md` interno al `exclude`. Actualizar la lista que `check_site.py:258-264`
   verifica.
6. Enlazar `llms.txt` desde el footer de todas las plantillas y añadirlo a
   `robots.txt`.
7. `sync-web.ps1:104-108`: registrar `python build_news_sitemap.py` en el flujo
   (aunque siga con `ACTIVATED = False`).

### Fase 1 — Google: verificación y propiedad (S)

8. Crear la propiedad **URL-prefix** en Search Console
   (`oasislocal.github.io/O.A.S.I.S./`). Google devuelve un meta tag →
   insertarlo en las plantillas compartidas y en cada HTML estático, y añadir un
   check en `check_site.py` que verifique que **todas** las páginas lo llevan.
9. Registrar Bing Webmaster Tools **importando desde GSC** (sin tocar HTML).
10. En GSC: enviar `sitemap.xml`, fijar el país objetivo (España) y el idioma, y
    dejar anotado que el informe de Core Web Vitals es la métrica de referencia.
11. Declarar en `docs/` el motivo por el que la verificación por DNS o por
    fichero en la raíz no es posible hoy (ver §9).

### Fase 2 — Datos estructurados honestos (M)

Trabaja sobre `index.html` y `_layouts/default.html`. Un único `@graph` por
página, con `@id` cruzados (`#website`, `#org`, `#app`, `#webpage`, `#breadcrumb`).

12. `Organization`: `name` normalizado a `O.A.S.I.S.`, `url`, `logo`,
    `sameAs: [GitHub releases, GitHub repo, Discussions, Issues, RSS, feed]`.
    Este es el item de mayor impacto: es lo que consolida la entidad y habilita
    el nombre de sitio y el panel de conocimiento.
13. `WebSite`: añadir `inLanguage` ya presente, `publisher` por `@id`, y
    `potentialAction` **sólo** si el buscador interno volviera (no aplica).
14. `SoftwareApplication`: completar el conjunto de propiedades de §1.3#13. No
    añadir `aggregateRating` (bloqueado por política de claims). Sí declarar
    `isAccessibleForFree: true` para Personal y `releaseNotes` → `changelog.html`.
15. `pricing.html`: añadir `Product` + `Offer` (precio 0 EUR para Personal,
    coherente con `index.html:42` y con lo que dice `pricing.html`). Nada de
    "Max a la venta" si no lo está: usar `availability` honesta.
16. `BreadcrumbList` en todas las páginas que la tengan + `BlogPosting` con
    `dateModified` real (commit de la última edición del `.md`), `articleSection`
    y `wordCount` generado.
17. `SiteNavigationElement` en el nav principal. `DefinedTermSet` + `DefinedTerm`
    para el glosario cuando exista `/glossary/`.
18. Migrar el `sameAs` de `about.html:41-43` al grafo de la home y añadir un
    `Person` sólo si hay alguien identificable que lo sea.

### Fase 3 — AEO/GEO: ser citable por las IAs (M)

19. `robots.txt`: política explícita y comentada de rastreadores de IA.
    **Permitir explícitamente los de cita/búsqueda** (OAI-SearchBot,
    Claude-SearchBot, PerplexityBot, Google-Extended, Bingbot) porque es la
    decisión de negocio que hace que la web aparezca en ChatGPT, Claude,
    Perplexity, Copilot y AI Overviews. **Decidir aparte los de entrenamiento**
    (GPTBot, ClaudeBot, CCBot): es una llamada editorial, no técnica. Dejar la
    decisión escrita en el propio `robots.txt` y en un `docs/` brief.
20. `llms.txt`: mantenerlo vivo y derivado de `site-data.json` + `VERSION`, no
    escrito a mano. Enlazado (Fase 0#6) y declarado en `robots.txt`.
21. Formato "answer-first" en las páginas que ya existen y convertirán:
    - `requirements.html`: primera tabla = "¿Puedo ejecutarlo con mi equipo?"
    - `models.html`: tabla de modelos con una fila de decisión
    - `comparison.html`: tabla comparativa por criterio
    - `faq.html`: cada respuesta a 2-3 frases antes del detalle
    - `security.html` / `privacy.html`: las tres primeras frases son la respuesta
22. Una sola fuente de verdad de la versión: `VERSION` + `site-data.json`.
    `llms.txt:2` dice "v0.2.0" hardcodeado; hoy es correcto por casualidad.

### Fase 4 — Bing, IndexNow e índices independientes (S, con bloqueo en §9)

23. `sync-web.ps1`: tras cada push, calcular las URLs nuevas/cambiadas
    (`build_sitemap.py` ya sabe qué cambió) yarlas a IndexNow **cuando exista
    dominio** (Fase 9). Dejar el hook escrito y desactivado, con el motivo
    documentado: en `oasislocal.github.io` el host es compartido por todos los
    proyectos Pages del usuario y la llave por host no es fiable.
24. Bing Webmaster: importar desde GSC, enviar el sitemap, activar la
    verificación por IndexNow cuando haya dominio.
25. Mojeek: es un índice independiente, acepta rastreadores, baja competencia y
    muy alta relevancia para consultas técnicas. Añadir su aviso de rastreo en
    Search Console (tiene flujo oficial) y comprobar que no lo bloquea el
    `robots.txt` resultante.
26. Marginalia y Yep: sólo verificación manual de que el sitio es rastreable.
    Sin trabajo ongoing.
27. `Yandex` queda excluido a propósito: IndexNow sí lo cubre, pero el mercado
    no es objetivo. Dejarlo en el envío genérico de IndexNow, sin esfuerzo extra.

### Fase 5 — Core Web Vitals (S)

28. `.lighthouserc.json`: añadir preset `mobile` (o un segundo fichero
    `.lighthouserc.mobile.json` que ya existe y no se usa), subir
    `numberOfRuns` a 3, y añadir aserciones de `largest-contentful-paint`,
    `cumulative-layout-shift`, `interaction-to-shift`/`total-blocking-time`.
29. Meter las páginas `/es/*` y `/blog/` en la lista de URLs medidas.
30. Medir y decidir sobre las 6 woff2: preloadeo de las críticas,
    `font-display: swap`, o subconjunto. El sitio es la mitad del argumento
    ("rápido porque es local"): el Core Web Vitals tiene que estar a la
    altura de la promesa.

### Fase 6 — Contenido y autoridad (L — el motor de crecimiento)

Sin contenido no hay nada que citar. Es la fase que más rinde y la que más
juego de herramientas exige.

31. **Extraer el inventario de herramientas a datos.** `_data/tools.yml` como
    fuente única (nombre, categoría, qué hace, riesgo, plan, descripción larga).
    `tools.html` se pasa a generarse desde ahí; el gemelo ES sigue `build_es.py`
    + `i18n/`. Todo en un commit, sin cambiar URLs.
32. **Páginas por herramienta** (`/tools/<slug>.html`), con contenido propio:
    qué hace, cuándo usarla, qué permiso pide, qué pasa si falla. Es la palanca
    más grande: convierte "100+ tools" en ~100 páginas indexables que
    responden a búsquedas de intención concreta.
33. **`/models/<modelo>.html`** para los perfiles ya declarados en
    `models.html`, y **`/requirements/` por nivel de hardware** (VRAM/RAM) a
    partir de la tabla existente en `requirements.html`.
34. **`/glossary/`** con un ancla por término desde `_data/journal_terms.json` +
    `tooltips.json` + `JOURNAL_GLOSSARY.md`, marcado como `DefinedTermSet`.
    Responde a "qué es X", que es donde las IAs citan.
35. **`/compare/<alternativa>.html`** a partir del patrón de `comparison.html`,
    sólo con afirmaciones verificables (`check_claims.py` sigue siendo el juez).
36. **Journal**: seguir `JOURNAL_CHECKLIST.md` hasta 20-30 piezas con formato de
    pregunta→respuesta corta→detalle, cada una con ≥3 enlaces internos
    (ya lo exige `check_site.py`) y su gemelo ES.
37. Regla de oro de esta fase: cada página nueva nace con su gemelo ES en el
    mismo commit, o `check_site.py` frena el push.

### Fase 7 — Medición sin trackers (M)

38. GitHub Action con cron que llama a la **Search Console API**
    (`searchanalytics.query`) con una service account en Secrets y escribe
    `metrics/search.json` con agregados: consultas, páginas, país, dispositivo,
    CWV. Cero JavaScript en el sitio, cero cookies, cero requests de terceros
    para el visitante.
39. Publicar sólo agregados y **filtrar las consultas** (nada de query strings
    con datos personales). `METRICS.md` se actualiza con esta vía como la
    respuesta oficial a "sin trackers".
40. `METRICS.md:59-65` (targets de launch) se reemplaza por la línea base real
    de GSC, no por objetivos inventados.

### Fase 8 — Google News (S, opcional)

Ya está construido. Son 4 pasos de `GOOGLE_NEWS.md:36-53` más el cableado en
`sync-web.ps1`. Se activa **después** de tener el Journal con cadencia real: un
news sitemap con 0 artículos dentro de la ventana de 48 h no aporta nada y da
ruido. Dejarlo anotado y no priorizado.

### Fase 9 — Cuando llegue el dominio real (S, bloqueado hasta entonces)

41. `CNAME` en el repositorio de despliegue + HTTPS.
42. **301** de `oasislocal.github.io/O.A.S.I.S./**` a la raíz del dominio.
    Antes: mapa URL→URL completo y revalidación de hreflang/canonical.
43. Reescribir `robots.txt` y `sitemap.xml` con el dominio final.
44. **IndexNow**: aquí sí. Llave de 8-128 caracteres alojada en la **raíz del
    host** (`/<key>.txt`), que es el requisito que hoy no se puede cumplir.
45. GSC **Domain property** por TXT de DNS (cubre http/https/www/subdominios y
    ambas versiones del sitio).
46. Verificación de Bing por TXT o fichero en raíz.
47. Decidir `www` vs apex, y activar HSTS.

---

## 4. Matriz de capacidades

| Capacidad | Estado | Acción | Fase |
|---|---|---|---|
| Rastreo / rastreo presupuesto | correcto | — | — |
| Sitemap completo EN+ES | parcial (21 URLs, sin ES) | emitir gemelos ES | 0 |
| `lastmod` fiable | falso (constante) | derivar de git | 0 |
| Índice canónico | duplicado en legales | consolidar | 0 |
| Verificación GSC | ausente | meta tag en 40 páginas | 1 |
| Verificación Bing | ausente | importar desde GSC | 1 |
| `Organization` + `sameAs` | débil | grafo único + sameAs | 2 |
| `SoftwareApplication` | incompleto | 13 propiedades | 2 |
| `Product`/`Offer` en pricing | ausente | añadir, con disponibilidad honesta | 2 |
| Rich result Software App | **inalcanzable** (pide reseñas) | esperar reseñas reales | 2 |
| FAQ rich result | **muerto** desde 05-2026 | mantener markup como estructura | 2 |
| `BreadcrumbList` / `BlogPosting` | correcto | sólo `dateModified` real | 2 |
| Datos de imagen (Image Search) | **cero `<img>`** | capturas reales + `ImageObject` + sitemap de imágenes | 6 |
| Paquete de vídeo | no aplica | sólo si hay vídeo | — |
| Paquete local / GBP | no aplica | sin dirección física | — |
| Core Web Vitals | sólo desktop, sin presupuesto | preset mobile + aserciones CWV | 5 |
| AI Overviews | sin atajo | contenido verificable + CWV + estructura | 3, 6 |
| Citas en ChatGPT / Claude / Perplexity / Copilot | por omisión | política explícita de `robots.txt` + `llms.txt` vivo | 3 |
| IndexNow | bloqueado (host compartido) | hook preparado | 4, 9 |
| Mojeek / Marginalia / Yep | sin presencia | verificación de rastreo | 4 |
| Google News | construido y dormido | activar con cadencia real | 8 |
| Analítica | prohibida por promesa | GSC API en Actions | 7 |
| Dominio propio | bloqueado | CNAME + 301 + llave IndexNow + DNS TXT | 9 |

---

## 5. Orden de ejecución y dependencias

```
Fase 0 (fugas)  ──► Fase 1 (GSC+Bing) ──► Fase 5 (CWV)
      │                                        │
      ├─► Fase 2 (JSON-LD) ───────────────────┤
      │         │                             │
      │         └─► Fase 3 (AEO/robots) ─► Fase 6 (contenido) ──► Fase 8 (News)
      │
      └─► Fase 4 (Bing/independientes) ──────────────────────────► Fase 7 (métricas)
                                        Fase 9 (dominio) desbloquea F4 y parte de F1
```

- Nada de la Fase 6 depende de un dominio: es contenido, se puede empezar ya.
- La Fase 7 es la que permite decidir las Fases 6 y 8 con datos en vez de con
  intuición. Si el tiempo es corto, invertir el orden: F7 antes que F6.
- La Fase 9 no se planifica en detalle hasta tener el dominio; lo de arriba es
  el esqueleto, no el trabajo.

## 6. Verificación

```powershell
#Puertas obligatorias antes de cualquier push (ya las llama sync-web.ps1)
python check_site.py        # enlaces, hreflang, sitemap, pares EN/ES
python check_claims.py      # frases prohibidas, métricas sin medir
python build_sitemap.py --check

# Nuevas, a añadir en este plan
python check_seo.py         # JSON-LD válido, og/twitter, meta de verificación,
                            # unicidad de title/description, reciprocidad
                            # hreflang, robots.txt, noindex en 404
```

`check_seo.py` debe entrar en `sync-web.ps1` en el mismo bloque que los otros
dos. Mientras no exista, el comentario de `sync-web.ps1:75-78` es incorrecto y
hay que corregirlo (hallazgo #21).

Verificación manual tras desplegar (una vez al trimestre):

- GSC → Informes → Rendimiento: 28 días, contrastar con la línea base de §F7.
- GSC → Core Web Vitals: los tres campos en verde.
- GSC → Inspeccionar URL: las 5 URLs de referencia (home, tools, models,
  pricing, un post del Journal), EN y ES.
- GSC → Enhancements: el informe que sobreviva (sólo queda Software App, y
  sabemos que está bloqueado) — usar la auditoría de Rich Results Test como
  diagnóstico de validez, no como promesa de resultado.
- Comprobación de citas: preguntar a ChatGPT, Perplexity, Claude y Copilot
  "¿qué asistente de IA local para Windows existe?" y registrar si la web
  aparece. Es la métrica honesta de AEO.

## 7. Riesgos

| Riesgo | Mitigación |
|---|---|
| El subpath de `github.io` limita la verificación y bloquea IndexNow | Fases 1 y 4 se resuelven con la vía disponible; Fase 9 cierra el resto |
| Contenido a escala (`/tools/*`) yDuplicate content o thin content | Cada página con contenido propio y datos desde `_data/tools.yml`, nunca plantillas vacías |
| Fase 6 crece sin control y rompe el `sync-web.ps1` | `check_site.py` y `check_claims.py` como puertas; nunca se saltan |
| Prometer rich results que no llegan (Software App, FAQ) | Documentado en §2; ningún texto del sitio afirma un rich result |
| Que la web empiece atrackear para "medir mejor" | `METRICS.md` es la política; la Fase 7 es la única vía aprobada |
| Deriva entre `llms.txt`, `site-data.json` y `VERSION` | Generar `llms.txt` desde los datos |

## 8. No objetivos (decidido explícitamente)

- **Buscador interno en la web.** Descartado. Google Custom Search JSON API
  está cerrada a nuevos clientes y caduca el 1-ene-2027; el widget hosted
  introduciría un script de Google y una cookie, rompiendo la promesa.
- **Datos estructurados para rich results ya muertos**: HowTo, speakable,
  Sitelinks Searchbox, FAQPage como rich result.
- **Indexing API de Google** (sólo JobPosting/BroadcastEvent).
- **Google Business Profile / paquete local**: no hay dirección física.
- **Yandex como mercado objetivo**: cubierto gratis por IndexNow, sin esfuerzo adicional.
- **Analytics de terceros**: prohibido.

## 9. Por qué Fase 9 está bloqueada (documentado para no reintentarlo)

En `oasislocal.github.io/O.A.S.I.S.`:

1. **GSC por fichero** → exige el fichero en la raíz del host
   (`oasislocal.github.io/google<token>.html`). No está en nuestro árbol.
2. **GSC por DNS** → exige un TXT en el DNS de `oasislocal.github.io`. No somos
  Proprietarios de `github.io`.
3. **IndexNow** → la llave debe servirse en la raíz del host, y el protocolo
   asume una llave por host. `oasislocal.github.io` es compartido por todos los
   proyectos GitHub Pages del usuario: una llave ahí no es fiable ni
   representativa.
4. **Llave única, dos sitios** → si mañana conviven `github.io` y el dominio
   propio, cada host necesita la suya.

Todo lo anterior se resuelve con un dominio propio. Nada de esto se puede
atajar antes, y no se debe reintentar en fase 1.

---

## 10. Backlog (fuera de alcance, anotado para cuando haya margen)

- `VideoObject` si algún día hay un demo en vídeo (short de 60 s, subtítulos).
- Google Analytics **opt-in** por el visitante, si alguna vez se acepta romper la
  promesa (no recomendado).
- Traducción a más idiomas con el pipeline `build_es.py` como plantilla.
- Sitemap de imágenes propio cuando haya capturas reales.
- Rich result de Software App, cuando existan reseñas orgánicas verificables.
