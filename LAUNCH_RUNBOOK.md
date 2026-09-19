# LAUNCH_RUNBOOK.md

> **Internal. Not published.** Launch sequence and the exact commands.
> Website phases are controlled by `launch.json` / `sync-web.ps1`.

---

## States

| State | What visitors see | How to deploy |
|---|---|---|
| `teaser` | Only the teaser shell (waitlist). Nothing else exists on the server. | `.\sync-web.ps1 -Mode teaser` |
| `countdown` | Only the countdown to the reveal date. | `.\sync-web.ps1 -Mode countdown -RevealDate "YYYY-MM-DDTHH:MM:SSZ"` |
| `live` | The full site. | `.\sync-web.ps1 -Mode live` |

**Important:** editing `launch.json` alone does **not** deploy. The script rebuilds
the snapshot; non-live deploys contain *only* the shell (verified: no full-site
files are reachable, not even in view-source).

---

## Timeline

### T-7 — Teaser
- [ ] `launch.json` → `mode: teaser`, run `sync-web.ps1`.
- [ ] Verify: `/` shows teaser; `download.html` → 404.
- [ ] Announce teaser on GitHub / socials (link to the root URL).

### T-3 — Show the substance
- [ ] Publish 2 journal posts: "What is a local AI assistant" + "How O.A.S.I.S. works locally".
- [ ] Confirm the homepage shows: local model, agent loop, permissions.
- [ ] Re-run QA_CHECKLIST §2.

### T-1 — Countdown
- [ ] Set the reveal date (`launch.json.revealDate`, ISO-8601 UTC).
- [ ] `sync-web.ps1 -Mode countdown -RevealDate "<date>"`.
- [ ] Verify countdown ticks and the date is correct in your timezone.

### T0 — Launch
- [ ] `sync-web.ps1 -Mode live`.
- [ ] Verify (HTTP): `/`, `/download.html`, `/tools.html`, `/models.html`, `/privacy.html`, `/security.html`, `/blog/`, `/sitemap.xml`, `/robots.txt` → all 200; internal docs (`PRODUCT_TRUTH.md`, `CLAIMS_AUDIT.md`) → 404.
- [ ] Publish the GitHub release with installer + SHA256 + notes.
- [ ] Update the repo README (proprietary notice + link to site).
- [ ] Post announcement (GitHub Discussions, socials).
- [ ] Watch for the first download and the first permission dialog report.

### T+1 / T+3 / T+7 — Content
- [ ] T+1: "How O.A.S.I.S. works locally"
- [ ] T+3: "Permissions and safety"
- [ ] T+7: "Local AI on ordinary hardware"

---

## Max (phase 49)
Max is **not on sale**. Keep the site saying *"Max isn't on sale yet — join the
waitlist."* Before opening sales:
- [ ] Checkout URL + licence delivery
- [ ] Terms + refund policy
- [ ] Price locked (€15 → €25 at 1.0)
- [ ] Replace the waitlist CTA with the purchase CTA
- [ ] Update `PRODUCT_TRUTH.md` and every price mention

---

## Rollback
Any bad deploy: `.\sync-web.ps1 -Mode live` (or the previous phase) rebuilds the
snapshot from `main`. The deploy branch is disposable — never hand-edit it.
