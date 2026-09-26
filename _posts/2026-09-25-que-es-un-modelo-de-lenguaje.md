---
title: "¿Qué es un modelo de lenguaje?"
ref: what-is-a-language-model
lang: es
permalink: /es/blog/2026/09/25/que-es-un-modelo-de-lenguaje/
tags: [basics]
series: foundations
order: 2
reading_minutes: 7
excerpt: "De dónde sale la capacidad de un modelo de lenguaje, qué son los miles de millones de números que lleva dentro, y qué explica su comportamiento."
---

[La vez anterior](/es/blog/2026/09/25/que-es-la-ia-y-como-funciona/) llegamos
hasta "predice el siguiente trozo de texto". Es cierto, y también es el principio
y no el final, porque enseguida aparecen tres preguntas:

1. ¿De dónde sale esa capacidad?
2. ¿Qué hay realmente dentro del modelo?
3. ¿Y por qué se comporta como se comporta?

Este artículo responde a las tres. No da por sabido nada.

## Parte 1 — La versión corta

### Viene de leer. Muchísimo.

Un modelo de lenguaje se <span class="term" data-term="training">entrena</span>
con texto: libros, páginas web, código, foros, manuales, transcripciones. No con
reglas, sino con ejemplos y ajustándose muy poco, millones de veces cada vez que
su predicción falla.

El resultado no es una base de datos de frases. Es un conjunto de números que
codifica cómo tiende a comportarse el lenguaje. El modelo nunca guarda "la
capital de Francia es París" como un dato que pueda consultar. Guarda una forma
que hace que eso sea **probable**.

### El modelo son los números, y los números son el modelo

Dentro de un modelo de lenguaje no hay palabras. No hay letras, ni frases, ni
imágenes, ni base de datos. Hay una lista de números —miles de millones, sus
<span class="term" data-term="parameters">parámetros</span>— en un archivo de tu
disco, normalmente de unos pocos gigabytes. Esos números son lo que el
entrenamiento ajustó. Son todo el modelo, y ese archivo es el
<span class="term" data-term="model-file">archivo de modelo</span>.

### De ahí salen tres comportamientos, y nada más

{% capture behaviours %}
<table class="cmp-table">
  <thead>
    <tr>
      <th scope="col">Lo que ves</th>
      <th scope="col">Lo que es en realidad</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">"Sabe" datos</th>
      <td>El patrón que aprendió casualmente encaja con esos datos</td>
    </tr>
    <tr>
      <th scope="row">"Olvida" en una charla larga</th>
      <td>El principio se salió de su
        <span class="term" data-term="context-window">ventana de contexto</span></td>
    </tr>
    <tr>
      <th scope="row">A veces inventa</th>
      <td>La continuación más fluida no es la más cierta</td>
    </tr>
  </tbody>
</table>
{% endcapture %}
{% include components/callout.html type="note" title="Tres comportamientos, una causa" body=behaviours %}

Ninguno es un misterio en cuanto aceptas que no hay base de datos ni memoria.
Hay una función sobre números, llamada una y otra vez, token a token.

El vocabulario es fijo y finito, así que el modelo realmente elige entre un
número finito de palabras. Elige la que mejor continua el patrón, y esa palabra
puede ser rara.

## Parte 2 — Un nivel más profundo, todavía sencillo

### Entrenamiento: ajustar una predicción, millones de veces

Toma una frase. Tapa la última palabra. Pide al modelo que la adivine. Adivina, y
la predicción es incorrecta, o correcta, o aproximada. Este es todo el bucle:

1. Muéstrale al modelo un trozo de texto real.
2. Produce una predicción para cada token posible siguiente.
3. Se mide cuánto se equivocó. Esa distancia respecto a la verdad es lo que el
   entrenamiento intenta reducir.
4. Se ajustan **todos** los parámetros un poco, en la dirección que habría
   mejorado la predicción.
5. Se repite con otro trozo, en miles de máquinas a la vez, durante semanas.

Nadie escribe la gramática, los datos ni el razonamiento. Todo emerge de la
estadística del texto, y esa es la razón de que el modelo pueda estar
equivocado con seguridad: si el patrón que aprendió está equivocado, la salida
se equivoca con esa misma seguridad fluida.

{% capture cutoff %}
Los datos de entrenamiento son una fotografía de un momento. Un modelo no puede
saber nada publicado el día en que se entrenó, y no te avisará de ello. Esa fecha
es su <span class="term" data-term="knowledge-cutoff">corte de conocimiento</span>,
y es la razón de que un asistente debería poder decirte lo que no sabe en lugar
de adivinar.
{% endcapture %}
{% include components/callout.html type="warning" title="Tiene fecha, y no te la dice" body=cutoff %}

### Parámetros y archivo de modelo

Los parámetros, más el vocabulario, más algo de configuración, se guardan como el
archivo de modelo. Ese es el artefacto completo.

La consecuencia práctica: elegir qué modelo se ejecuta es elegir qué archivo se
carga en tu disco. Puedes borrarlo, moverlo, probar otro y ejecutarlo con la red
desenchufada. En el momento de la consulta no se descarga nada.

Que un modelo publique sus números ya entrenados es una pregunta distinta de si
su código es abierto, y las dos se confunden constantemente:

{% capture weights %}
Un modelo con <span class="term" data-term="open-weights">pesos
abiertos</span> te deja descargar e inspeccionar los números entrenados. Normalmente
**no** publica el código de entrenamiento ni los datos. Por eso "pesos abiertos" y
"código abierto" son afirmaciones distintas, y por eso la licencia de un modelo no
es la licencia de la app. La [página de modelos](/es/models.html) detalla qué
licencias se aplican a cada cosa.
{% endcapture %}
{% include components/callout.html type="note" title="Pesos abiertos no es código abierto" body=weights %}

### Tokens: el alfabeto con el que trabaja de verdad

Antes de llegar al modelo, el texto se corta en
<span class="term" data-term="token">tokens</span>: trozos que suelen ser una
palabra, parte de una palabra o un trozo de puntuación. El corte lo hace un
<span class="term" data-term="tokenizer">tokenizador</span>, y es la razón de que
todo producto de IA cobre "por token".

De ahí salen dos cosas:

- Un token no es un carácter. El modelo no ve la ortografía. No puede notar que
  una palabra y su plural comparten letras.
- El corte pierde información de una manera que importa: las palabras comunes son
  un token, los nombres raros varios, y el coste de una petición sigue ese
  reparto.

### Contexto: lo único que puede ver

Todo lo que sabe de tu conversación llega en su entrada: la instrucción, los
archivos que adjuntaste, los mensajes hasta ahora. El tamaño máximo de esa
entrada es la ventana de contexto.

No hay nada detrás. Cuando haces scroll hacia arriba no se recuerda nada, porque
el texto se vuelve a enviar cada vez. Una conversación larga puede empujar el
principio fuera de la ventana, y el modelo se comportará como si nunca hubiera
ocurrido.

La solución habitual no es una ventana mayor. Es **apuntar las cosas**: notas, un
resumen, un archivo. No es un truco, es simplemente cómo funciona el mecanismo.

{% capture sizes %}
<tbody>
  <tr><th scope="row">1.5B parámetros</th><td data-value="1.0">1.0</td></tr>
  <tr><th scope="row">3B parámetros</th><td data-value="2.0">2.0</td></tr>
  <tr><th scope="row">4B parámetros</th><td data-value="2.5">2.5</td></tr>
  <tr><th scope="row">8B parámetros</th><td data-value="4.8">4.8</td></tr>
</tbody>
{% endcapture %}
{% include components/chart.html body=sizes chart="bar" unit=" GB" title="Un modelo más grande es un archivo más grande" sub="Cuantización Q4, los perfiles que incluye la app" note="Tamaños de descarga declarados de los archivos cuantizados, no benchmarks medidos. Las cifras exactas salen del propio archivo de cada modelo y cambian con la cuantización." %}

Un modelo que aprende de más parámetros guarda más patrones. No se vuelve
automáticamente más correcto: primero se vuelve más pesado, y la descarga que ves
es el precio. Si te preguntas cuánto pesa un archivo concreto, la
[página de modelos](/es/models.html) lista los perfiles que incluye la app, y
[requisitos](/es/requirements.html) explica cuánta RAM y VRAM necesita cada uno
para cargarse.

### Muestreo: el único sitio donde entra la elección

El modelo devuelve una probabilidad para cada token. Después se elige uno, y ese
paso se llama <span class="term" data-term="sampling">muestreo</span>. Es una
decisión de la aplicación, no del modelo, y es a lo que se refiere la gente cuando
habla de la "creatividad" de un modelo. Misma instrucción, dos ajustes:

{% include components/tabs.html id="temperature-demo" aria-label="Temperatura comparada" labels="Temperatura baja|Temperatura alta" panels="El modelo casi siempre toma el token más probable. Obtienes la respuesta obvia, igual cada vez.

Eso es lo que quieres para código, para extraer datos de un documento y para todo aquello donde una respuesta sorprendente cueste más que una aburrida. También es más rápido, porque el camino probable es el más rápido para el hardware.

`temperatura: 0.1` — la misma respuesta siempre, y esa respuesta suele ser la correcta.|La cola improbable puede hablar. Obtienes más variedad, más sorpresa y más opciones de que algo se lea bien y no signifique nada.

Útil cuando quieres opciones en lugar de una respuesta: generar nombres, redactar varios tonos, explorar un problema. Inútil cuando equivocarse es caro.

`temperatura: 1.2` — tres respuestas distintas a una sola instrucción, y quizá una de ellas está equivocada de una forma nueva." %}

{% capture why_temp %}
No es un cerebro distinto. Es la misma aritmética con más distribución autorizada a
hablar. El ajuste lo pone el software que rodea al modelo, y por eso el mismo
modelo se comporta de forma distinta en dos aplicaciones.
{% endcapture %}
{% include components/callout.html type="tip" title="Un modelo, dos personalidades" body=why_temp %}

## Entonces, ¿por qué se comporta así?

Porque todos los comportamientos que nos parecen raros tienen la misma
explicación: hay un patrón, y no hay tabla de consulta.

- **No puede comprobarse a sí mismo.** No tiene nada contra lo que comprobarse.
- **Se repite** cuando la temperatura es baja y el patrón es fuerte.
- **Inventa citas** porque una cita plausible es una continuación plausible.
- **Olvida entre sesiones** porque no se apunta nada, salvo algo externo que lo
  apunte.

Nada de eso es una lista de errores. Es la misma lista de consecuencias.

{% capture faq2 %}
- **¿Por qué olvida el principio de una conversación larga?**
  Porque el principio se salió de la ventana de contexto, y detrás de la ventana
  no hay memoria. Apunta lo importante y lo leerá cada vez.

- **¿Se puede evitar que invente?**
  No pidiéndoselo. Dale una fuente que leer y una forma de enseñar qué usó, y la
  invención baja mucho.

- **¿Un modelo más grande siempre es mejor?**
  No. Guarda más patrones, necesita más memoria y responde más despacio. Más es un
  intercambio, no una mejora.

- **¿En qué se miden los parámetros?**
  En miles de millones, escritos "7B" o "4B". Cuenta números, no habilidades.

- **¿Necesito el modelo más nuevo?**
  Normalmente no. Un modelo más pequeño que responde en menos de un segundo en tu
  propia <span class="term" data-term="gpu">GPU</span> es más útil a diario que
  uno grande al que hay que esperar.
{% endcapture %}
{% include components/details.html title="Preguntas sobre modelos" faq="true" open="first" body=faq2 open-label="Abrir todo" close-label="Cerrar todo" %}

## En corto

- Un modelo de lenguaje es una lista de números, ajustados leyendo muchísimo texto
  hasta que sus predicciones fueron lo bastante buenas.
- No lleva ninguna base de datos dentro, así que no hay nada que consultar ni
  contra qué comprobarse.
- Su comportamiento se deduce de tres hechos: predice, solo ve lo que está en su
  entrada, y elige entre un vocabulario fijo.
- Qué modelo se ejecuta es qué archivo está en tu disco. Por eso puede funcionar
  con la red desenchufada.

**Siguiente en esta serie:** *Tokens y ventana de contexto* — el mecanismo detrás
del coste, de los límites de longitud y de esa forma tan extraña que una
conversación larga olvida su propio principio. Lo estamos escribiendo; el
[índice del Journal](/es/blog/) lista lo que ya ha salido.

<!--
Series: foundations
Number: 2 of 40
Next: tokens-and-the-context-window (ref: tokens-and-the-context-window)
Pillar page: /es/models.html (este artículo es el concepto; la página es el producto)
-->
