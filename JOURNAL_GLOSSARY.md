# Journal glossary — EN → ES

Machine-readable version: [`_data/journal_terms.json`](_data/journal_terms.json)
(read by `check_claims.py`, and available to the blog templates as
`site.data.journal_terms`). This file is the human-readable version.

**Rule that matters most:** the Spanish renderings below are the ones already
live on the published `es/` pages. Consistency with the existing site beats
literal translation. If a term is not listed here, look at how the term is
already written in `es/*.html` and reuse that.

## Terms that stay in English

`token` · `embedding` · `workflow` · `sandbox` · `local-first` · `offline-first` ·
`on-device` · `RAM` · `VRAM` · `GGUF` · `Docker` · `MCP` · `Ollama` · `LM Studio`

The site writes *"sandbox aislado"*, not *"entorno aislado"*, and *"alto
impacto"*, not *"alto riesgo"*. Do not invent new renderings.

> Known inconsistency (legacy, to fix when a page is next touched): `es/faq.html`
> says "flujos de trabajo" in one place where the rest of the site says
> "workflows". The glossary wins: **workflow**.

## Core vocabulary

| English | Español |
|---|---|
| artificial intelligence | inteligencia artificial |
| AI assistant | asistente de IA |
| language model | modelo de lenguaje |
| large language model (LLM) | modelo de lenguaje grande (LLM) |
| chatbot | chatbot |
| context window | ventana de contexto |
| token / tokenization / tokenizer | token / tokenización / tokenizador |
| inference | inferencia |
| training | entrenamiento |
| fine-tuning | ajuste fino |
| hallucination | alucinación |
| temperature | temperatura |
| retrieval-augmented generation (RAG) | generación aumentada por recuperación (RAG) |
| vector store | almacén de vectores |
| prompt / system prompt | instrucción / instrucción de sistema |
| prompt injection | inyección de instrucciones |
| quantization | cuantización |
| parameters | parámetros |
| benchmark | prueba de rendimiento |
| tokens per second | tokens por segundo |
| cold start | arranque en frío |
| GPU offloading | descarga a GPU |
| screen analysis | análisis de pantalla |
| speech to text / text to speech | de voz a texto / de texto a voz |
| wake word | palabra de activación |
| voice cloning | clonación de voz |
| persistent memory | memoria persistente |
| high-impact tool | herramienta de alto impacto |
| confirmation | confirmación |
| destructive action | acción destructiva |
| open source / proprietary | código abierto / propietario |
| telemetry | telemetría |
| self-funded | autofinanciado |

## Marking terms so the tooltip glossary works

The site ships a 69-term tooltip dictionary. Highlight a term in an article
with the existing markup, in the language of the article:

```html
<span class="term" data-term="llm">language model</span>
<span class="term" data-term="ventana de contexto">ventana de contexto</span>
```

Usable `data-term` keys for the Foundation articles: `llm`, `model`, `token`,
`context-window`, `inference`, `embedding`, `on-device`, `local-ai`,
`local-first`, `offline`, `cloud`, `agent`, `tool`, `memory`, `runtime`,
`model-size`, `persistent-memory`, `semantic-search`, `stt`, `tts`, `vision`,
`ocre` → `ocr`, `quantization`, `gguf`, `ram`, `vram`, `gpu`, `cpu`,
`permission`, `high-impact`, `sandbox`, `isolation`, `network`,
`proprietary`, `open-source`, `telemetry`, `personal`, `max`, `workflow`,
`ollama`, `lm-studio`, `llama-cpp`, `hugging-face`.

## Forbidden phrasings

Enforced by `check_claims.py`. Each one exists because `PRODUCT_TRUTH.md` says
so, not for style.

| id | never write | why |
|---|---|---|
| `never-leaves-pc` | "nothing ever leaves your PC", "nada sale de tu PC" | The app is offline-first, **not** network-blind |
| `product-wide-offline` | "completely offline", "totalmente sin conexión" as a product claim | True per feature (chat, voice, memory, documents), not product-wide |
| `zero-network` | "zero network activity", "cero actividad de red" | Web search, weather and integrations do use the network when invoked |
| `any-gguf` | "any GGUF runs", "cualquier GGUF funciona" | Say "compatible GGUF models" |
| `conscious-ai` | "the AI understands", "la IA entiende" | It predicts text; keep the mechanism visible |
| `free-forever-max` | "Max is available", "Max está a la venta" | Max is not on sale yet |

**Approved wording**, when a Journal article has to talk about the network:

> Local features run on your PC. Network-enabled features communicate
> externally only when you use or configure them. O.A.S.I.S. is offline-first,
> not network-blind.

> Las funciones locales se ejecutan en tu PC. Las funciones que usan red se
> comunican externamente solo cuando tú las usas o configuras. O.A.S.I.S. es
> offline-first, no ciego a la red.

## Performance numbers

A benchmark in a Journal article is only publishable together with a recorded
measurement: model, quantization, hardware, RAM, VRAM, context length and date.
The article must contain a visible *"How this was measured"* block with those
fields. `check_claims.py` fails the build if a speed or size figure appears in a
post without that block.

## Adding a term

1. Add the Spanish rendering to `terms` in `_data/journal_terms.json`.
2. Add the row to the table above.
3. Re-run `python check_claims.py`.
