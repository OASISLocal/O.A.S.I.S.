# Journal publication checklist

One page, per article. Work top to bottom. The automated gates
(`check_site.py`, `check_claims.py`) cover the mechanical part; what is left
is the part that needs judgement and a human eye.

## 1. Content rules

- [ ] **Part 1 is readable on its own.** Someone who stops after Part 1 still
      has the whole idea. Part 2 only deepens.
- [ ] **No overlap with a site page.** The Journal explains *concepts*;
      `how-it-works`, `requirements`, `models`, `tools`, `security`,
      `comparison`, `pricing`, `features`, `faq` explain *the product*. The
      article links to one of them instead of repeating it.
- [ ] **Every factual claim traced to a source.** `PRODUCT_TRUTH.md` is
      authoritative and derived from code. If a sentence cannot be traced, cut
      it or mark it as planned.
- [ ] **No anthropomorphising.** "It predicts the next token", not "it
      understands".
- [ ] **No performance figure without a measurement block** (model,
      quantization, hardware, RAM, VRAM, context, date) in a visible
      *"How this was measured"* section.
- [ ] **Forbidden phrasings** absent: see `JOURNAL_GLOSSARY.md`.
- [ ] **Max described honestly** as not on sale yet; **licence described as
      proprietary** where the topic touches licensing.
- [ ] **CTA is soft.** One link to the page that applies the concept, and one
      link to the next article in the series. No popups, no fake scarcity.

## 2. Metadata

- [ ] Filename `YYYY-MM-DD-<slug>.md`; the slug is what ends up in the URL.
- [ ] `title` ≤ 45 characters (the layout appends `" | O.A.S.I.S. Journal"`).
- [ ] `ref` set, and **identical in the English and the Spanish file** — this is
      what pairs them.
- [ ] `lang: en` / `lang: es`.
- [ ] `excerpt` ≤ 160 characters, written by hand (it is the meta description
      and the index listing, not a truncation of the body).
- [ ] `tags`: one from the series vocabulary — `basics`, `internals`,
      `privacy`, `models`, `hardware`, `safety`, `ecosystem`, `company`,
      `engineering`.
- [ ] Spanish post has an explicit `permalink:` under `/es/blog/...`.

## 3. Body

- [ ] Starts with `##`, never with `#` (the layout already renders the H1).
- [ ] Headings are `##`/`###` only, in order, no level skipped.
- [ ] ≥ 3 internal links that resolve to real pages.
- [ ] Key terms marked with the tooltip markup, using a `data-term` that exists
      in `tooltips.json`: e.g. `<span class="term" data-term="llm">…</span>`.
- [ ] "In short" closing section with three points.
- [ ] Next-in-series link at the end (or an explicit note that it is the first
      article).

## 2b. Components

When an article uses a component, `COMPONENTES.md` has the syntax. Three rules
that are not obvious and that break the build if forgotten:

- [ ] **A `{% raw %}{% capture %}{% endraw %}` parameter cannot contain a double
      quote.** `-Message "your message"` inside a double-quoted include argument
      produces *"Invalid syntax for include tag"* and only shows up at build
      time. `check_seo.py` now catches the unbalanced quote, but the fix is to use
      single quotes in the example.
- [ ] **Tables and chart bodies are HTML, not markdown.** kramdown wraps block
      content in `<p>`, and a `<p>` inside a `<table>` is invalid markup that
      fails the Jekyll build.
- [ ] **The `<table class="cmp-table">` class is written by the author**, not
      added by the script: the layout rules must be in force before JavaScript
      runs, and they are what keeps a wide table inside its scroll box on a
      phone.
- [ ] After adding or editing a component, open
      `/blog/2026/09/25/every-component-on-one-page/` and look at it. That page
      is `noindex` and exists exactly for this.

## 4. Spanish version (assisted translation)

- [ ] Full translation, not a summary and not a machine dump.
- [ ] Glossary renderings used as in `JOURNAL_GLOSSARY.md`; nothing invented.
- [ ] No English scaffolding left: no "Part", "Level", "Step", "In short".
- [ ] Em dashes and quotation marks follow the house style used in `es/*.html`.
- [ ] Product name written `O.A.S.I.S.` or `OASIS`, never translated.

## 5. Automated gates (must be green before deploy)

```
python build_sitemap.py          # sitemap includes the new URLs
python check_site.py
python check_claims.py
powershell -ExecutionPolicy Bypass -File .\sync-web.ps1 -Message "..."
```

- [ ] CI green: *Deploy Jekyll*, *Lighthouse CI*, *pages build and deployment*.
- [ ] In production: EN 200, ES 200, `hreflang` cross-links both ways, the post
      appears in `/blog/` and `/es/blog/` **without** the `EN` badge, the Atom
      feed has the entry, and the old post URLs still 404.

## 6. After publishing

- [ ] Update the reverse links: the pillar page the article belongs to now links
      to it (2–3 articles per pillar page, 14 EN + 14 ES).
- [ ] If the article belongs in `llms.txt`, add it there too.
- [ ] Check Search Console the next day: indexed? any crawl error?
