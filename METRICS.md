# METRICS.md

> **Internal. Not published.** What we measure, and how — without betraying the
> product promise.

---

## The constraint

The website says **"no trackers on this page"** and the app ships **telemetry
off by default**. That is a selling point. So we do **not** add:
Google Analytics, Plausible, pixels, heatmaps, fingerprinting, or any script
that runs on the visitor's machine.

**Measure where the data already exists, off-site.**

---

## Data sources we already have

| Funnel stage | Metric | Source | Privacy |
|---|---|---|---|
| Acquisition | Repo views, clones, referrers | GitHub Insights → Traffic | Aggregated by GitHub |
| Acquisition | Stars | GitHub API (`★ N on GitHub`, already on site) | Public |
| Activation | Installer downloads | GitHub Releases asset `download_count` | Public |
| Activation | Release asset views | GitHub Releases page | Aggregated |
| Conversion | Waitlist signups (+ interest split) | Cloudflare KV → `/export` CSV | First-party, consented |
| Retention | Issues/discussions opened by users | GitHub | Public |
| Technical | Crashes / permission errors | **Not collected by default.** Only if a user sends a diagnostics export or reports an issue | User-initiated |

---

## What "activation" can and cannot be measured

Without telemetry we cannot know first-launch or first-prompt counts remotely.
Accepted trade-off — the plan prioritises trust over dashboards.

Proxy signals:
- download count vs. stars ratio,
- issues mentioning successful setup,
- waitlist conversion,
- discussions activity.

If deeper funnel data is ever wanted, the **only** honest option is an
**opt-in** diagnostic the user explicitly enables, mirroring the app's existing
optional diagnostics webhook (`config.telemetry_enabled = False` by default).

---

## Reading the numbers

- `site-data.json` and `roadmap.json` states must not be inferred from metrics.
- Never publish a metric that cannot be reproduced from a public source.
- Any metric shown on the site (stars) must degrade gracefully — it already hides
  the strip if the API fails.

---

## Targets for launch week (informal)
| Metric | Goal |
|---|---|
| Installer downloads (first 7 days) | baseline to beat, not a vanity target |
| Waitlist signups | ≥ 25% of downloads? measure, don't assume |
| Issues with actionable bug reports | track count + resolution time |
| First community PR / discussion | ≥ 1 |
