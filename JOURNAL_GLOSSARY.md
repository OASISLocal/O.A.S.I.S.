# Journal glossary — EN → ES

Two files, two jobs:

- [`tooltips.json`](tooltips.json) and [`tooltips.es.json`](tooltips.es.json) are
  the **glossary**: every term, its Spanish rendering, its category and where it
  is explained. These are the only hand-edited glossary files.
- [`_data/journal_terms.json`](_data/journal_terms.json) is the **claims rules**:
  forbidden phrasings and the approved wording, read by `check_claims.py` and
  available to the templates as `site.data.journal_terms`.

The visible glossary at `/glossary/` and `/es/glossary/`, plus their JSON-LD, are
**generated** from the two dictionaries by `build_glossary.py`. Do not edit them
by hand; the `--check` mode fails the deploy if they drift.

**Rule that matters most:** the Spanish renderings in `tooltips.es.json` are the
ones already live on the published `es/` pages. Consistency with the existing site
beats literal translation. If a term is not there yet, look at how it is already
written in `es/*.html` and reuse that.

## Terms that stay in English

`token` · `embedding` · `workflow` · `sandbox` · `local-first` · `offline-first` ·
`on-device` · `RAM` · `VRAM` · `GGUF` · `Docker` · `MCP` · `Ollama` · `LM Studio`

Machine-readable copy: `keep_in_english` in
[`_data/journal_terms.json`](_data/journal_terms.json).

The site writes *"sandbox aislado"*, not *"entorno aislado"*, and *"alto
impacto"*, not *"alto riesgo"*. Do not invent new renderings.

> Known inconsistency (legacy, to fix when a page is next touched): `es/faq.html`
> says "flujos de trabajo" in one place where the rest of the site says
> "workflows". The glossary wins: **workflow**.

## Core vocabulary

Do not keep a copy of the EN → ES table here. It was 30 rows of hand-maintained
duplication that silently fell behind the dictionaries, and the generated page
already shows every term with its Spanish rendering side by side:

- English: [`/glossary/`](https://oasislocal.github.io/O.A.S.I.S./glossary/)
- Spanish: [`/es/glossary/`](https://oasislocal.github.io/O.A.S.I.S./es/glossary/)

Terms the Journal teaches are listed in both, each linking to the page that
explains it.

## Marking terms so the tooltip glossary works

The site ships a **77-term** tooltip dictionary. Highlight a term in an article
with the existing markup, in the language of the article:

```html
<span class="term" data-term="llm">language model</span>
<span class="term" data-term="context-window">ventana de contexto</span>
```

`data-term` is always the **English key**, in both languages, because there is
one dictionary per language rather than one per spelling. The visible word is
whatever reads naturally in that language.

### The dictionary is generated, not maintained by hand

`tooltips.json` and `tooltips.es.json` are the only hand-edited files. From them
`build_glossary.py` generates the two visible pages **and** the two JSON-LD data
files:

```
python build_glossary.py            # regenerate
python build_glossary.py --check    # fail if stale; run by sync-web.ps1
```

It also validates, on every run, that each term's destination page exists in
**both** languages and that any `#anchor` in the link really exists on the page
it points to. So a term cannot be added with a dead destination.

That validation exists because the two things it would have caught did happen:
both pages once showed the same wrong definition in all 68 rows, and all 68
"Details" links were broken (the page lives at `/glossary/`, so a bare
`models.html` resolves to `/glossary/models.html`).

### Adding a term

1. Add it to **both** `tooltips.json` and `tooltips.es.json`, same `cat`.
2. Point `link` at a page that exists. For a concept the Journal teaches, link
   the article that teaches it; `build_glossary.py` resolves the Spanish twin
   automatically through the shared `ref`.
3. Run `python build_glossary.py` and commit all four generated files.

Categories are `AI`, `MODEL`, `HARDWARE`, `SOFTWARE`, `SECURITY`, `NETWORK`,
`PRODUCT`, and they set the order of the page.

### Concepts deliberately not in the dictionary yet

`fine-tuning`, `RAG` and `structured output` are taught by articles that are not
written yet. They get a term when the article lands, so that no tooltip ever
points at a page that does not exist.

## Forbidden phrasings

Enforced by `check_claims.py`. Each one exists because `PRODUCT_TRUTH.md` says
so, not for style. The `id` column is the one to use when adding a rule.

| id | never write | why |
|---|---|---|
| `never-leaves-pc` | "nothing ever leaves your PC", "nada sale de tu PC" | The app is offline-first, **not** network-blind |
| `product-wide-offline` | "completely offline", "totalmente sin conexión" as a product claim | True per feature (chat, voice, memory, documents), not product-wide |
| `zero-network` | "zero network activity", "cero actividad de red" | Web search, weather and integrations do use the network when invoked |
| `any-gguf` | "any GGUF runs", "cualquier GGUF funciona" | Say "compatible GGUF models" |
| `conscious-ai` | "the AI understands", "la IA entiende" | It predicts text; keep the mechanism visible |
| `max-on-sale` | "Max is available", "Max está a la venta" | Max is not on sale yet |

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
