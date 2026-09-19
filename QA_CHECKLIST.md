# QA_CHECKLIST.md

> **Internal. Not published.** Verification runbook for the website + product
> claims. Tick items only with evidence (command output, screenshot, test run).
>
> Owner: maintainer · Last run: 2026-09-19 · v0.2.0

---

## 1. Product QA (phases 32-37) — needs a Windows machine

### 1.1 Installation matrix (phase 34)
| Case | Steps | Expected | Status |
|---|---|---|---|
| Windows 10 clean | Install from release `.exe` | Installs, first run opens, onboarding appears | ☐ |
| Windows 11 clean | Same | Same | ☐ |
| CPU-only | Install + small model (Qwen 1.5B) | Chat works, slower; voice works | ☐ |
| NVIDIA | Install + Gemma 4B | Faster; GPU used (`/api/sysinfo` shows GPU) | ☐ |
| No Docker | Skip Docker | Everything except sandbox/code execution works | ☐ |
| With Docker | Start Docker Desktop | Code sandbox runs | ☐ |
| No internet after install | Unplug, then chat/voice/memory/files/Pc control | All local features work | ☐ |
| Installer hash | `certutil -hashfile OASIS.exe SHA256` | Matches published SHA256 | ☐ |

### 1.2 Privacy test (phase 35) — reproducible
1. Start O.A.S.I.S., note network usage (Task Manager → Performance → Ethernet/Wi-Fi).
2. Disconnect internet.
3. Use: chat, voice, memory recall, read a file, change volume, take a screenshot, run a local workflow.
4. **Expected:** all work; zero errors about network.
5. Reconnect, run `internet_search`.
6. **Expected:** network activity appears *only* here.

Record: date, build, observations. Attach to `CLAIMS_AUDIT.md` as evidence.

### 1.3 Permission tests (phase 36) — automated, in repo
Run: `python -m pytest tests/test_security_negative.py -q`
Expect **7 passed**. Covers:
- unapproved high-impact tools never execute,
- `deny` blocks,
- `confirm` does not run without approval,
- Free plan cannot run code tools,
- max-privacy mode blocks capture tools,
- published high-impact list == code list.

### 1.4 Negative security tests (phase 37)
| Attempt | Expected |
|---|---|
| Execute code with no permission | Blocked (`Confirmation required`) |
| Delete files unapproved | Blocked |
| Shut down unapproved | Blocked |
| Write file unapproved | Blocked / follows permission |
| Access screen with max privacy | Blocked |
| Enable mic without permission | Blocked |

Document each with a screenshot of the confirmation dialog.

---

## 2. Web QA (phases 18-19, 38-40)

### 2.1 Responsive (phase 18)
Capture at **320, 375, 390, 430, 768, 1024, 1366, 1920** px. Pass criteria:
- no horizontal scroll, no cut text, no element hidden without reason,
- hero, app mockup, tool tables, pricing, comparison, FAQ, footer all readable.
```powershell
# example: 320 CSS px via device scale
& $chrome --headless=new --force-device-scale-factor=3 --window-size=960,2100 --screenshot=out.png URL
```

### 2.2 Accessibility (phase 38)
- [ ] One `<h1>` per page, no heading-level skips (script: heading order).
- [ ] Keyboard: Tab/Shift+Tab/Enter/Space/Escape through nav, menu, FAQ, waitlist, theme toggle.
- [ ] Focus visible everywhere; never lost (skip target has `tabindex="-1"`).
- [ ] Screen reader: headings, buttons, nav, forms, status updates announced.
- [ ] All inputs have labels (explicit or wrapping `<label>`).
- [ ] `prefers-reduced-motion` disables animations and stages demos visible.
- [ ] Contrast ≥ 4.5:1 (light and dark).
- [ ] Zoom 100 / 125 / 150 / 200 % — no clipping.
- [ ] Automated: run the project's `scripts/a11y_audit.ps1` (axe) if available.

### 2.3 SEO (phase 39)
- [ ] Unique title + meta description per page.
- [ ] Canonical on every page.
- [ ] `sitemap.xml` lists all pages; `robots.txt` points to it.
- [ ] Open Graph + Twitter card per page; OG image exists.
- [ ] JSON-LD valid: SoftwareApplication (home), FAQPage (faq), BreadcrumbList (tools/models), BlogPosting (journal).
- [ ] Internal links resolve (script: internal link audit).
- [ ] No `noindex` on public pages; exactly one `h1`.

### 2.4 Performance (phase 19)
- [ ] Fonts load non-blocking (`media="print" onload`).
- [ ] No render-blocking JS; scripts at end of body.
- [ ] Page HTML < 100 KB/page; CSS < 15 KB; JS < 5 KB.
- [ ] No unoptimised raster images (currently none — keep it that way or add WebP/AVIF + width/height + lazy).
- [ ] Lighthouse (manual run): Performance/A11y/Best Practices/SEO ≥ 90.

### 2.5 Link audit (phase 40)
- [ ] Download → releases/latest resolves.
- [ ] GitHub, Discussions, Docs, EULA, Privacy Policy, Third-party notices.
- [ ] Journal, Changelog, Roadmap anchors.
- [ ] Waitlist endpoint responds.
- [ ] No link to a removed file (`roadmap.json`, `web/`, `pricing.md`, `funciones.html`).

---

## 3. Release readiness (phase 33 / 48)
- [ ] Installer + SHA256 published in the release.
- [ ] Release notes follow the template (highlights/added/improved/fixed/security/known issues).
- [ ] Known issues listed honestly.
- [ ] Model licences are distinct from the app licence (stated on `/models`).
- [ ] Legal: EULA, Privacy Policy, License, Third-party notices reachable.
- [ ] Refund policy documented before Max goes on sale.
