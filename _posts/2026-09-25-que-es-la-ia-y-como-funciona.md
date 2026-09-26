---
title: "¿Qué es la IA? Y cómo funciona"
ref: what-is-ai-and-how-it-works
lang: es
permalink: /es/blog/2026/09/25/que-es-la-ia-y-como-funciona/
tags: [basics]
series: foundations
order: 1
reading_minutes: 7
excerpt: "Qué es la IA en realidad, en dos niveles: la versión simple (predice el siguiente trozo de texto) y otra más profunda (tokens, probabilidades, contexto)."
---

Hay mucho ruido alrededor de la "inteligencia artificial". Este artículo es
deliberadamente silencioso. Explica qué hace un
<span class="term" data-term="llm">modelo de lenguaje</span>, en dos pasadas: la
primera es la idea entera en lenguaje claro, la segunda baja un nivel más y
todavía se detiene antes de las matemáticas.

Si lees la primera parte, ya está. La segunda está para el que tenga curiosidad.

{% capture one_liner %}
Un modelo de lenguaje hace una sola cosa: continúa texto. Todo lo que llamamos
"inteligencia" es esa única capacidad aplicada a problemas distintos, más una
cantidad enorme de ejemplos de cómo suele ser la respuesta.
{% endcapture %}
{% include components/callout.html type="note" title="La idea entera, en una caja" body=one_liner %}

## Parte 1 — En un minuto

### Es autocompletado, con una memoria muy larga

Conoces la sensación. Escribes media frase en una app de mensajes y te ofrece el
resto de la palabra. Eso es todo lo que hace un modelo de lenguaje, salvo que el
que usas cada día sin darte cuenta ha leído unos cientos de miles de millones de
frases, y en lugar de adivinar una palabra adivina el siguiente *trozo de
frase*, una y otra vez, hasta que ha escrito algo.

No hay un segundo mecanismo oculto.

### Predice; no consulta nada

Esto es lo que sorprende a la gente. El modelo no lleva dentro una base de
datos de hechos, ni una lista de países con sus capitales, ni notas sobre ti.
Tiene un conjunto de números —decenas de miles de millones, sus
<span class="term" data-term="parameters">parámetros</span>— que codifican los
*patrones* del lenguaje: cómo suelen seguirse las palabras, qué frases son
plausibles y cuáles no lo son.

Cuando te dice un dato, no lo lee de una tabla. Produce texto que encaja con el
patrón. A menudo es exactamente correcto. A veces no, y el resultado es una
frase fluida, segura y equivocada. Eso tiene nombre, y conviene saberlo pronto:

{% capture hallu %}
Una **alucinación** no es un error que se corrija con una actualización. Es lo que
pasa cuando un sistema sin base de datos dentro produce el texto más
plausible en lugar de un dato comprobado. La solución nunca es "pídeselo por
favor": es darle algo con lo que comprobar, que es otro diseño.
{% endcapture %}
{% include components/callout.html type="warning" title="Por qué inventa" body=hallu %}

### Por qué eso basta para ser útil

Si lo único que sabe es "continuar esto bien", ¿cómo se convierte en un
asistente? Porque casi cualquier tarea que le pedirías a una máquina tiene forma
de texto. El mecanismo es idéntico en las cuatro filas; solo cambia el
envoltorio.

{% capture four_tasks %}
<table class="cmp-table">
  <thead>
    <tr>
      <th scope="col">Lo que pides</th>
      <th scope="col">Lo que significa aquí "continuar el texto"</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Resume este PDF</th>
      <td>Producir un texto más corto que conserve lo importante</td>
    </tr>
    <tr>
      <th scope="row">Explícame este error</th>
      <td>Producir texto que encaje con "una persona competente explicando un error"</td>
    </tr>
    <tr>
      <th scope="row">Traduce esto</th>
      <td>Producir texto en el otro idioma que encaje con el significado</td>
    </tr>
    <tr>
      <th scope="row">Reescribe este correo</th>
      <td>Producir texto con el mismo significado y otro tono</td>
    </tr>
  </tbody>
</table>
{% endcapture %}
{% include components/callout.html type="tip" title="Cuatro tareas, un mecanismo" body=four_tasks %}

Por eso el mismo modelo de base puede resumir un contrato, explicar código y
redactar una respuesta, sin que nunca se le haya "entrenado para ser asistente".

### Lo que no es

- **No entiende nada.** No hay un momento en el que el significado haga clic. Es
  aritmética sobre números, y el buen resultado es que la aritmética produzca
  algo que se lee como comprensión.
- **No consulta nada**, así que no puede comprobar si acierta.
- **No te recuerda entre conversaciones.** Cada conversación nueva empieza de
  cero salvo que algo externo al modelo apunte notas.
- **No es magia ni es una base de datos.** Es una función muy grande que
  convierte texto en una predicción.

## Parte 2 — Un poco más profundo, todavía simple

Ahora el mecanismo, en el mismo lenguaje claro, paso a paso.

### Tu texto se corta en tokens

Un modelo no lee letras ni palabras enteras. El texto se corta primero en
<span class="term" data-term="token">tokens</span> mediante un
<span class="term" data-term="tokenizer">tokenizador</span>: trozos que suelen ser
una palabra, parte de una palabra o un trozo de puntuación. Por eso todo
producto de IA cobra "por token".

El corte también pierde información de una manera interesante: **los tokens son
todo lo que el modelo llega a ver**. No hay letras dentro del modelo, ni
palabras, ni frases. Un modelo no puede ni remotamente notar que "dog" y "dogs"
comparten letras.

### Cada token se convierte en una lista de números

Cada token se busca en una tabla y se convierte en una lista larga de números:
desde unos cientos hasta un par de miles. Esos números son un
<span class="term" data-term="embedding">embedding</span>: una posición en un
espacio de significado, donde lo que se comporta igual en el lenguaje queda
cerca.

Este es el paso que más sorprende: **el mundo entero del modelo es una lista de
números**. Sin texto, sin imágenes, sin base de datos, solo aritmética sobre
esos números.

### Produce una probabilidad para cada token posible

Tras leer tu texto, el modelo da una puntuación a cada token que conoce, y luego
normaliza esas puntuaciones en probabilidades que suman 100%.

Si escribes *"La capital de Francia es"*, ocurre algo parecido a esto:

{% capture probs %}
<tbody>
  <tr><th scope="row">París</th><td data-value="94">94%</td></tr>
  <tr><th scope="row">la</th><td data-value="3">3%</td></tr>
  <tr><th scope="row">también</th><td data-value="1">1%</td></tr>
  <tr><th scope="row">un</th><td data-value="1">1%</td></tr>
  <tr><th scope="row">cualquier otra cosa</th><td data-value="1">1%</td></tr>
</tbody>
{% endcapture %}
{% include components/chart.html body=probs chart="bar" unit="%" title="Una respuesta, y una cola muy larga" sub="Distribución ilustrada tras «La capital de Francia es»" note="Cifras inventadas, elegidas para mostrar la forma y no para medir un modelo: casi toda la masa en un token, y una cola fina donde viven los errores. Las distribuciones reales cambian según el modelo y la formulación." %}

El modelo no está eligiendo entre una lista de *respuestas*. Está eligiendo el
siguiente trozo de texto, y en este caso cualquier continuación sensata de esa
frase resulta ser la respuesta. Ordena la columna y la cola queda a la vista: las
respuestas plausibles pero equivocadas están todas en el último por ciento.

### Se elige una: esa es la única "elección"

Un token con 94% suele ser el que sale. No está garantizado, y ahí es donde vive
el ajuste de <span class="term" data-term="temperature">temperatura</span>:

- **Temperatura baja** → casi siempre el token más probable. Repetitivo, plano,
  predecible. Lo adecuado para código y para datos.
- **Temperatura alta** → la cola improbable puede aparecer. Más variado, más
  sorprendente, con más opciones de no tener sentido.

Así que la "creatividad" en un modelo de lenguaje no es un cerebro distinto. Es
la misma aritmética con las colas de la distribución autorizadas a hablar. El
paso en el que se elige se llama
<span class="term" data-term="sampling">muestreo</span>, y pertenece al software
que rodea al modelo, no al modelo.

### La ventana de contexto: solo ve los últimos N tokens

Todo lo que el modelo sabe de *tu* conversación llega en su entrada: la
instrucción, los archivos que adjuntaste, los mensajes hasta ahora. El tamaño
máximo de esa entrada es la
<span class="term" data-term="context-window">ventana de contexto</span>.

Detrás no hay memoria. Cuando haces scroll hacia arriba no está "recordando"
nada: el texto se vuelve a enviar cada vez. Dos consecuencias que conviene
interiorizar:

- Una conversación larga puede empujar el principio fuera de la ventana, y el
  modelo se comportará como si nunca hubiera ocurrido.
- Llenar la ventana no es gratis. Las entradas más grandes son más lentas y
  necesitan más memoria. La ventana de contexto es un presupuesto que gastas,
  no una capacidad que tienes.

### "Entrenar" es ajustar esos números

Un modelo empieza como números aleatorios. Alguien lo
<span class="term" data-term="training">entrena</span> mostrándole muchísimo
texto y, después de cada fragmento, ajustando cada número un poco en la
dirección que habría hecho más probable el token correcto. Repite eso durante
meses en miles de máquinas y los números aleatorios producen lenguaje fluido.

Nadie programa la gramática, los datos ni el razonamiento. Emergen de la
estadística del texto. Esa es también la razón de que un modelo pueda estar
equivocado con seguridad: si el patrón que aprendió está equivocado, la salida
se equivoca con esa misma seguridad fluida.

### La misma idea, otro ordenador

Nada de lo anterior necesita un centro de datos. Los números pueden vivir en un
servidor o en un archivo de tu disco, y la
<span class="term" data-term="inference">inferencia</span> —el bucle de generar
el siguiente token— se ejecuta donde estén esos números, en tu
<span class="term" data-term="cpu">CPU</span> o tu
<span class="term" data-term="gpu">GPU</span>.

Lo único que cambia es el contexto: qué modelo, de qué tamaño, a qué velocidad, y
qué más necesita la red. La versión honesta de esa diferencia está en
[el modelo de privacidad](/es/privacy.html), y lo que de verdad pasa dentro de la
caja, en [Cómo funciona O.A.S.I.S.](/es/how-it-works.html).

## Qué cambia cuando se ejecuta en tu PC

Tres cosas concretas, sin adjetivos:

- El <span class="term" data-term="model">modelo</span> es un archivo de tu disco,
  no una petición al ordenador de otro. Qué modelo ejecutas es decisión tuya, y
  también [su tamaño](/es/models.html).
- Las funciones locales —chat, voz, memoria, documentos— se ejecutan
  <span class="term" data-term="on-device">en tu propio hardware</span> y siguen
  funcionando con la red desenchufada. Las funciones que usan red se comunican
  externamente solo cuando las usas. O.A.S.I.S. es
  <span class="term" data-term="offline-first">offline-first</span>, no ciego a
  la red.
- El [hardware](/es/requirements.html) deja de ser una abstracción y pasa a ser
  una restricción real. La <span class="term" data-term="ram">RAM</span>, la
  <span class="term" data-term="vram">VRAM</span> y el disco deciden qué modelos
  puedes ejecutar.

Si prefieres verlo a leerlo, la [beta es gratis](/es/download.html) y la
[lista completa de funciones](/es/features.html) cabe en una página, a propósito.

{% capture faq %}
- **¿Entiende lo que dice?**
  No. Produce texto que encaja con el patrón de lo que parece entender. Si eso es
  "comprender" es una pregunta de filosofía, no de ingeniería, y la respuesta
  honesta de ingeniería es que el mecanismo no tiene base de datos ni forma de
  comprobarse.

- **¿Por qué se equivoca si ha leído tanto?**
  Porque leer le da patrones, no datos. Un patrón puede estar equivocado con
  seguridad, y no hay nada dentro del modelo con lo que comparar.

- **¿Un modelo más grande sabe más?**
  Guarda más patrones, y necesita más memoria y más tiempo por respuesta. Más no
  es lo mismo que correcto.

- **¿De dónde sale entonces el conocimiento?**
  Del texto, ponderado por cuántas veces apareció cada cosa. Por eso un modelo
  tiene un <span class="term" data-term="knowledge-cutoff">corte de
  conocimiento</span>: no sabe nada publicado después del texto más reciente que
  vio.

- **¿Qué es la cuantización?**
  La <span class="term" data-term="quantization">cuantización</span> comprime los
  números para que el archivo pese menos y funcione con menos memoria, con un
  pequeño coste en calidad. Es la razón de que un modelo de 4B quepa en un
  portátil normal.
{% endcapture %}
{% include components/details.html title="Preguntas que se hacen de verdad" faq="true" open="first" schema="faqpage" body=faq open-label="Abrir todo" close-label="Cerrar todo" %}

## En corto

- Un modelo de lenguaje predice el siguiente trozo de texto. Todo lo demás es esa
  capacidad con distinto disfraz.
- Trabaja sobre números, no sobre comprensión, y no lleva base de datos con la
  que comprobarse: por eso puede estar equivocado con tanta seguridad.
- Que se ejecute en un centro de datos o en tu disco es una cuestión de *dónde
  viven los números*, no de lo listo que sea.

**Siguiente en esta serie:**
[¿Qué es un modelo de lenguaje?](/es/blog/2026/09/25/que-es-un-modelo-de-lenguaje/)
— la misma idea vista desde el archivo de modelo, los parámetros y los nombres
que la gente usa para ellos.

<!--
Series: foundations
Number: 1 of 40
Next: 2026-09-25-que-es-un-modelo-de-lenguaje.md (ref: what-is-a-language-model)
Pillar page: /es/how-it-works.html (este artículo es el concepto; la página es el producto)
-->
