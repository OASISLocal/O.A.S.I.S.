# CLAIMS_AUDIT.md

> **Internal. Not published.** Every material public claim, its category, source
> and last verification. Categories: **VERIFIED** · **QUALIFIED** · **PLANNED** ·
> **EXPERIMENTAL** · **ILLUSTRATIVE**.
>
> Last pass: 2026-09-19 · v0.2.0

| Claim (as published) | Category | Source | Verified | Notes |
|---|---|---|---|---|
| Windows 10/11 | VERIFIED | `installer/oasis.nsi` | 2026-09-19 | x64 only |
| Free beta, no account | VERIFIED | `config.py`, installer | 2026-09-19 | no account system exists |
| Works offline (local features) | QUALIFIED | `data_flow_audit.md` | 2026-09-19 | after model download; network tools excepted |
| 100+ tools | VERIFIED | `registry.py` (101 calls) | 2026-09-19 | 5 conditional |
| 10 high-impact tools | VERIFIED | `registry.py:188` | 2026-09-19 | always confirm |
| Voice in Spanish/English | VERIFIED | `core/voice.py`, `config.tts_language` | 2026-09-19 | Whisper + Kokoro |
| Screen analysis only when asked | VERIFIED | `vision_screen` tool is on-demand | 2026-09-19 | no background watcher for vision |
| Coding requires Max | VERIFIED | `Feature.CODE_MODE` | 2026-09-19 | explanations stay Personal |
| Sandbox requires Max | VERIFIED | `Feature.DOCKER_SANDBOX` | 2026-09-19 | + Docker installed |
| Vision requires Max | VERIFIED | `Feature.VISION` | 2026-09-19 | confirmed by owner |
| Workflows require Max | VERIFIED | `Feature.WORKFLOWS` | 2026-09-19 | confirmed by owner |
| Discord/Telegram require Max | VERIFIED | `Feature.MESSAGING` | 2026-09-19 | |
| Mobile/browser ext require Max | VERIFIED | `mobile_app`, `browser_extension` | 2026-09-19 | |
| External MCP servers require Max | VERIFIED | `Feature.MCP_SERVERS` | 2026-09-19 | |
| Max is a one-time payment (€15 → €25) | PLANNED | settings pricing card | 2026-09-19 | not on sale yet |
| No telemetry by default | VERIFIED | `config.telemetry_enabled=False` | 2026-09-19 | optional webhook only |
| Proprietary, not open source | VERIFIED | `legal/LICENSE.md` v1.3 | 2026-09-19 | repo public ≠ open source |
| 47 tok/s (demo) | ILLUSTRATIVE | demo mock only | 2026-09-19 | hardware dependent, labelled |
| €184.20 Q2 example | ILLUSTRATIVE | demo mock only | 2026-09-19 | labelled |
| "Up and running in ten minutes" | QUALIFIED | — | 2026-09-19 | depends on connection/hardware |
| Linux / macOS | PLANNED | roadmap | 2026-09-19 | no builds |
