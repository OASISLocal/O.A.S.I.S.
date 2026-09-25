---
title: "Every component, on one page"
ref: components-demo
lang: en
tags: [basics]
noindex: true
sitemap: false
excerpt: "Internal test page that exercises every Journal component: callouts, accordions, tables, charts, timeline, tabs, video and gallery."
reading_minutes: 3
---

This is an internal test page. It exists so every component can be checked in
the browser instead of being assumed to work. It is `noindex` and out of the
sitemap.

## Callouts

{% capture callout_note %}
A **note** is the neutral kind. Markdown works inside: *italics*, `code`, and
[this link](/how-it-works.html).
{% endcapture %}
{% include components/callout.html type="note" body=callout_note %}

{% capture callout_tip %}
A **tip** is for the thing that saves the reader time.
{% endcapture %}
{% include components/callout.html type="tip" title="Try this first" body=callout_tip %}

{% capture callout_warn %}
A **warning** is the only component allowed a colour, and it still carries a
word. Never rely on colour alone.
{% endcapture %}
{% include components/callout.html type="warning" body=callout_warn %}

{% capture callout_measured %}
| Field | Value |
|---|---|
| Model | Gemma 4B (Q4) |
| Hardware | 16 GB RAM, no GPU |
| Context | 4 096 |
| Date | 2026-09-25 |
{% endcapture %}
{% include components/callout.html type="measured" body=callout_measured %}

## Accordion

{% capture details_body %}
- **Does this work with JavaScript disabled?**
  Yes. Every component here is real HTML; the script only adds sorting, the
  lightbox, tabs and the chart drawing.
- **Why no Chart.js, Mermaid or GLightbox?**
  Because this site promises no trackers and no third-party requests. A CDN
  script would break that promise, and add a single point of failure.
- **Can I add my own component?**
  Yes: one template in `_includes/components/`, one file in
  `assets/components/`, and add its name to the detection list in
  `_layouts/post.html`.
{% endcapture %}
{% include components/details.html title="Questions" faq="true" body=details_body %}

## Tables

{% capture table_rows %}
<table>
  <thead>
    <tr>
      <th scope="col">Tier</th>
      <th scope="col" data-sort data-key="ram">RAM</th>
      <th scope="col" data-sort data-key="vram">VRAM</th>
      <th scope="col">What it runs</th>
    </tr>
  </thead>
  <tbody>
    <tr><th scope="row">Minimum</th><td>8 GB</td><td>none</td><td>Models up to ~3B, chat and voice</td></tr>
    <tr><th scope="row">Recommended</th><td>16 GB</td><td>4–8 GB</td><td>Models up to ~8B, vision included</td></tr>
    <tr><th scope="row">Comfortable</th><td>32 GB</td><td>12 GB+</td><td>Large models, everything at once</td></tr>
  </tbody>
</table>
{% endcapture %}
{% include components/table.html body=table_rows caption="Hardware tiers, as published on the requirements page" sortable="true" note="These are the app's declared requirements, not measured benchmarks. Click a header to sort." %}

## Chart

{% capture chart_rows %}
<tbody>
  <tr><th scope="row">Gemma 4B (Q4)</th><td data-value="4.1">4.1</td></tr>
  <tr><th scope="row">Llama 3.2 3B (Q4)</th><td data-value="2.0">2.0</td></tr>
  <tr><th scope="row">Qwen 2.5 1.5B (Q4)</th><td data-value="1.0">1.0</td></tr>
</tbody>
{% endcapture %}
{% include components/chart.html body=chart_rows chart="bar" unit=" GB" title="Download size of the bundled profiles" sub="Quantized to Q4, as declared by the app" note="Declared download sizes. Not a speed benchmark and not measured on any particular machine." %}

{% capture line_rows %}
<tbody>
  <tr><th scope="row">3B</th><td data-value="2.4">2.4</td></tr>
  <tr><th scope="row">4B</th><td data-value="4.1">4.1</td></tr>
  <tr><th scope="row">8B</th><td data-value="7.6">7.6</td></tr>
</tbody>
{% endcapture %}
{% include components/chart.html body=line_rows chart="line" unit=" GB" title="The same numbers, drawn as a line" sub="To prove the line renderer works" note="Same data as the bar chart above." %}

## Timeline

{% capture timeline_body %}
- **2026-09-20 · v0.2.0** — the Mono release: voice, memory, documents and everyday PC control.
- **2026-07-02 · v0.1.x** — first public beta, chat with compatible GGUF models.
- **Planned** — Linux build, Max early access.
{% endcapture %}
{% include components/timeline.html body=timeline_body %}

## Tabs

{% include components/tabs.html id="shell" labels="PowerShell|Bash" panels="Run it from the repository root, then push:

```powershell
.\sync-web.ps1 -Message "your message"
```

And from Bash:

```bash
./sync-web.ps1 -Message "your message"
```" %}

## Gallery

{% include components/gallery.html title="Screens from the site" aria-label="View larger" images="/assets/gallery/gallery-home.png|Home — the product page|Gateway view of the home page|/assets/gallery/gallery-home.png, /assets/gallery/gallery-privacy.png|Privacy — the per-feature table|The Local/Network table every feature is classified in|/assets/gallery/gallery-privacy.png, /assets/gallery/gallery-tools.png|Tools — the inventory|The tool list with its permission level and plan|/assets/gallery/gallery-tools.png" %}

## Video

{% include components/video.html id="oasis-local-demo" provider="youtube" title="O.A.S.I.S. running on Windows" poster="/assets/posters/shell-demo.png" caption="The click-to-load facade: no third-party request happens until the poster is clicked." note="The id below is a placeholder. A real post passes its own video id." %}
