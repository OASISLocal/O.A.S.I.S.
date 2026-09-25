---
title: "¿Qué es la IA? Y cómo funciona"
ref: what-is-ai-and-how-it-works
lang: es
permalink: /es/blog/2026/09/25/que-es-la-ia-y-como-funciona/
tags: [basics]
excerpt: "Qué es la IA de verdad, en dos niveles: la versión sencilla (predice la siguiente palabra) y una algo más profunda (tokens, probabilidades y contexto)."
---

Hay mucho ruido alrededor de la "inteligencia artificial". Este artículo es
deliberadamente silencioso. Explica qué hace un modelo de lenguaje en dos
pasadas: la primera es la idea entera en lenguaje llano; la segunda baja un
nivel y aun así se queda lejos de las matemáticas.

Lee la primera parte y ya está. La segunda está para quien tiene curiosidad.

## Parte 1 — En un minuto

### Es autocompletado, con una memoria muy larga

Ya conoces la sensación. Escribes media frase en una app de mensajes y te
ofrece el resto de la palabra. Eso es todo lo que hace un modelo de lenguaje,
salvo que la versión que usas cada día sin darte cuenta ha leído unos cientos
de miles de millones de frases, y en vez de adivinar una palabra adivina el
siguiente *trozo de frase*, una y otra vez, hasta que ha escrito algo.

Ese es todo el truco. No hay un segundo mecanismo escondido.

### Predice; no consulta nada

Esta es la parte que sorprende. El modelo no lleva dentro una base de datos de
datos, ni una lista de países con sus capitales, ni notas sobre ti. Lleva un
conjunto de números —decenas de miles de millones— que codifican los *patrones*
del lenguaje: qué palabras suelen seguir a cuáles, qué frases son plausibles,
cuáles son un despropósito.

Cuando te dice un dato, no lo está leyendo de una tabla. Está produciendo texto
que encaja con el patrón. A menudo es exactamente lo correcto. Otras veces no,
y el resultado es una frase fluida, segura y equivocada. Para eso hay nombre, y
en este Journal habrá un artículo entero sobre ello más adelante.

### Por qué eso basta para ser útil

Si lo único que sabes hacer es "seguir bien un texto", ¿cómo aparece un
asistente? Porque casi cualquier tarea que le pedirías a una máquina tiene
forma de texto:

- *Resume este PDF* → producir una versión más corta que conserve lo importante.
- *Explícame este error* → producir texto que encaje con "alguien competente explicando un error".
- *Traduce esto* → producir texto en el otro idioma que encaje con el significado.
- *Reescribe este correo* → producir texto con el mismo mensaje en otro tono.

Cada una es una tarea de continuación con un disfraz distinto. Por eso el mismo
modelo puede resumir un contrato, explicar código y redactar una respuesta, sin
que nadie lo entrenara nunca "para ser asistente".

### Lo que no es

- **No entiende nada.** No hay ningún momento en el que el significado "haga
  clic". Es aritmética sobre números, y el buen resultado es que la aritmética
  produzca algo que se lee como comprensión.
- **No consulta nada**, así que no puede comprobar si acierta.
- **No te recuerda entre conversaciones.** Cada conversación nueva empieza de
  cero, salvo que algo fuera del modelo tome notas.
- **No es magia ni una base de datos.** Es una función muy grande que convierte
  texto en una conjetura.

## Parte 2 — Algo más profundo, todavía sencillo

Ahora el mecanismo, en el mismo lenguaje llano, paso a paso.

### Tu texto se corta en tokens

Un modelo no lee letras ni palabras enteras. El texto se corta primero en
tokens: trozos de texto que suelen ser una palabra, o parte de una palabra, o un
trozo de puntuación. Eso lo hace un *tokenizador*, y es la razón por la que
todo producto de IA cobra "por token".

El corte tiene además una consecuencia interesante: **los tokens son todo lo que
el modelo llega a ver**. Dentro del modelo no hay letras, ni palabras, ni
frases. Un modelo literalmente no puede notar que "perro" y "perros" comparten
letras, salvo que esa relación ya estuviera capturada al convertir el texto.

### Cada token se convierte en una lista de números

Cada token se busca en una tabla y se convierte en una lista larga de números —
desde unos cientos hasta un par de miles de valores. Esos números son un
*embedding*: una posición en un espacio de significado, donde lo que se
comporta de forma parecida en el lenguaje queda cerca.

Este es el paso que más sorprende: **todo el mundo del modelo es una lista de
números**. No hay texto, ni imágenes, ni base de datos: solo aritmética sobre
esos números. Todo lo que un modelo de lenguaje sabe del mundo está guardado
como geometría en ese espacio.

### Produce una probabilidad para cada token posible

Después de leer tu texto, el modelo devuelve un número por cada token que
conoce: una puntuación de "qué probable es que esto venga ahora". Esas
puntuaciones se normalizan a probabilidades, así que suman 100.

Si escribes *"La capital de Francia es"*, pasa algo parecido a esto:

| Candidato | Probabilidad |
|---|---|
| París | 94% |
| está | 3% |
| también | 1% |
| una | 1% |
| cualquier otra cosa | 1% |

El modelo no está eligiendo entre una lista de *respuestas*. Está eligiendo el
siguiente trozo de texto, y en este caso cualquier continuación sensata de esa
frase resulta ser la respuesta.

### Se elige uno: esa es la única "decisión"

Un **token** con 94% suele ser el que te dan. Pero no está garantizado, y ahí
vive el famoso mando de temperatura:

- **Temperatura baja** → casi siempre el token más probable. Repetitivo, plano,
  predecible. Bien para código y para datos.
- **Temperatura alta** → la cola de la distribución tiene oportunidad de
  aparecer. Más variado, más sorprendente, con más opciones de no tener sentido.

Así que la "creatividad" de un modelo de lenguaje no es otro cerebro. Es la
misma aritmética permitiendo que hablen las colas de la distribución.

### La ventana de contexto: solo ve los últimos N tokens

Todo lo que el modelo sabe de *tu* conversación llega en su entrada: la
instrucción, los archivos que adjuntaste, los mensajes hasta ahora. El tamaño
máximo de esa entrada es la ventana de contexto.

No hay memoria detrás. Cuando haces scroll hacia arriba, el modelo no está
"recordando" nada: se está reenviando el texto cada vez. Dos consecuencias que
conviene interiorizar:

- Una conversación larga puede empujar el principio fuera de la ventana, y el
  modelo se comportará como si nunca hubiera ocurrido.
- Llenar la ventana no es gratis. Las entradas más grandes son más lentas y
  necesitan más memoria. La ventana de contexto es un presupuesto que gastas,
  no una capacidad que tengas.

### "Entrenar" es solo ajustar esos números

Un modelo empieza como números aleatorios. Después alguien le muestra una
cantidad enorme de texto y, tras cada fragmento, ajusta cada número un poco en
la dirección que habría hecho más probable el token correcto. Repite eso durante
meses en miles de máquinas, y los números aleatorios se convierten en algo que
produce lenguaje fluido.

Nadie programa la gramática, los datos ni el razonamiento. Emergen de la
estadística del texto. Esa es también la razón de que un modelo pueda
equivocarse con seguridad: si el patrón que aprendió está equivocado, la salida
se equivoca con esa misma seguridad fluida.

### La misma idea, en otro ordenador

Nada de lo anterior necesita un centro de datos. Los números pueden vivir en un
servidor o en un archivo de tu disco, y la inferencia —el bucle de generar el
siguiente token— se ejecuta donde estén esos números.

Lo único que cambia es el contexto: qué modelo, de qué tamaño, a qué velocidad
y qué más necesita la red. Escribimos sobre esa diferencia con honestidad en
[el modelo de privacidad](/es/privacy.html), y sobre la parte que ocurre dentro
de la caja en [Cómo funciona O.A.S.I.S.](/es/how-it-works.html).

## Qué cambia cuando se ejecuta en tu PC

Tres cosas concretas, sin adjetivos:

- El modelo es un archivo en tu disco, no una petición al ordenador de otra
  persona. Qué modelo ejecutas es decisión tuya, y [de qué tamaño](/es/models.html)
  también.
- Las funciones locales —chat, voz, memoria, documentos— se ejecutan en tu
  procesador y siguen funcionando con la red desenchufada. Las funciones que
  usan la red se comunican externamente solo cuando tú las usas. O.A.S.I.S. es
  offline-first, no ciego a la red.
- El [hardware](/es/requirements.html) deja de ser una abstracción y pasa a ser
  una restricción real: RAM, VRAM y disco deciden qué modelos puedes ejecutar.

Si prefieres verlo a leerlo, la [beta es gratis](/es/download.html) y la
[lista completa de funciones](/es/features.html) ocupa una página, a propósito.

## En corto

- Un modelo de lenguaje predice el siguiente trozo de texto. Todo lo demás es
  esa capacidad con distinto disfraz.
- Trabaja sobre números, no sobre comprensión, y no tiene ninguna base de datos
  con la que comprobarse: por eso puede estar equivocado con total fluidez.
- Que se ejecute en un centro de datos o en tu disco es cuestión de *dónde
  viven los números*, no de lo listo que sea.

**Siguiente en esta serie:** *¿Qué es un modelo de lenguaje (LLM?)* — la misma
idea vista desde el archivo del modelo, los parámetros y los nombres que la
gente usa. Lo estamos escribiendo; el [índice del Journal](/es/blog/) lista lo
que ya ha salido.

<!--
Series: foundations
Number: 1 of 40
Next: 2026-09-25-what-is-a-language-model.md (ref: what-is-a-language-model)
Pillar page: /how-it-works.html (este artículo es el concepto; la página es el producto)
-->
