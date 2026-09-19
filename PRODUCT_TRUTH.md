# PRODUCT_TRUTH.md

> **Internal document. Not published.** Single source of truth for every public
> claim on the website, README, FAQ and docs.
> Derived from code, not from marketing copy. If the website disagrees with this
> file, the website is wrong.
>
> Last verified: 2026-09-19 · against v0.2.0

---

## 1. Identity

| Field | Value | Source |
|---|---|---|
| Name | O.A.S.I.S. | brand |
| Meaning | Offline AI System for Information Sovereignty | brand |
| Version | v0.2.0 | `VERSION` |
| Status | Public beta | `CHANGELOG.md` |
| Platform | Windows 10 / 11 (x64) | installer `oasis.nsi` |
| License | **Proprietary** — not open source, not freeware in distributed form | `legal/LICENSE.md` v1.3 |
| Source availability | **Not public.** Repository is public for transparency/docs; code is not open source | `legal/LICENSE.md` |
| Distribution | Free edition + Max (one-time license). Max not on sale yet | `docs/FREE_MAX_FEATURES.md` |
| Executable | `OASIS.exe` | `installer/oasis.nsi` |
| Data folder | `%LOCALAPPDATA%\O.A.S.I.S.\` | `core/paths.py` |

## 2. Plans — authoritative matrix

Source of truth: `src/core/freemium.py` (`_FREE_FEATURES = {}`, `_PRO_FEATURES = all`).

> The project's own rule: *"El catálogo procede de src/core/freemium.py; no se
> mantiene una lista paralela en la interfaz."*

| Capability | Personal | Max | Feature flag | Status |
|---|:---:|:---:|---|---|
| Local chat (GGUF models) | ✅ | ✅ | — | Implemented |
| Local voice (STT + TTS) | ✅ | ✅ | — | Implemented |
| Basic RAG / memory | ✅ | ✅ | — | Implemented |
| Documents (PDF/DOCX/XLSX) | ✅ | ✅ | — | Implemented |
| Everyday PC control (low-risk tools) | ✅ | ✅ | — | Implemented |
| Projects | up to 3 | unlimited | `FREE_PROJECT_LIMIT=3` | Implemented |
| **Vision / screen analysis** | ❌ | ✅ | `vision` | Implemented |
| **Advanced RAG** | ❌ | ✅ | `advanced_rag` | Implemented |
| **Coding (full code agent)** | ❌ | ✅ | `code_mode` | Implemented |
| **Docker sandbox** | ❌ | ✅ | `docker_sandbox` | Implemented |
| **Workflows & automations** | ❌ | ✅ | `workflows` | Implemented |
| **Scheduled workflows** | ❌ | ✅ | `scheduled_workflows` | Implemented |
| Discord / Telegram | ❌ | ✅ | `messaging` | Implemented |
| Mobile app + LAN pairing | ❌ | ✅ | `mobile_app` | Implemented |
| Browser extension | ❌ | ✅ | `browser_extension` | Implemented |
| External MCP tool servers | ❌ | ✅ | `mcp_servers` | Implemented |
| Voice cloning / advanced voice | ❌ | ✅ | `voice_cloning` | Implemented |
| Semantic file map | ❌ | ✅ | `file_map` | Implemented |
| Encrypted sync | ❌ | ✅ | `encrypted_sync` | Implemented |
| OpenCode integration | ❌ | ✅ | `opencode_integration` | Implemented |
| Parallel sessions | ❌ | ✅ | `parallel_sessions` | Implemented |

### Confirmed decisions (product owner, 2026-09-19)

1. **Vision is Max.** `plan.md` was wrong; the code is correct. Site now matches code.
2. **Workflows (incl. scheduled) are Max.** Same: code is authoritative.
3. **Local backup is available generally** (Personal), not Max-gated. The old
   plan listing it under Max is deprecated.
4. **Coding:** full code agent + sandbox = Max. Personal keeps code *explanations*
   and answering coding questions (no execution).

## 3. Tools

| Fact | Value | Source |
|---|---|---|
| Registered tools | **101 `register()` calls**, 5 conditional → ~100 active | `core/tools/registry.py` |
| Public figure | **100+ tools** (use this everywhere) | decision · verified 2026-09-19 |
| High-impact (always confirm) | **10**: `custom_command, system_control, kill_process, system_cleanup, clipboard_control, code_agent, python_sandbox, file_manager, run_workflow, git_ops` | `registry.py:188` |

> **Code fixes made while verifying (2026-09-19):**
> - `PRIVACY_SENSITIVE_TOOLS` listed the removed tool `recording`; replaced with
>   the real capture tools (`transcribe_meeting`, `video_frame`) so max-privacy
>   mode actually blocks them.
> - `CODE_TOOLS` listed `open_code`, which no longer exists; corrected to
>   `opencode`, so the Max gate applies to the real tool.
> - `tests/test_security_negative.py` added: asserts unapproved high-impact tools
>   never run, deny/permission gating works, Free can't run code tools, privacy
>   mode blocks capture tools, and the high-impact list matches what we publish.

## 4. Local / Network matrix

| Feature | Local | Needs internet | External service |
|---|:---:|:---:|:---:|
| Chat (local model) | ✅ | No | No |
| Voice (STT/TTS) | ✅ | No | No |
| Memory | ✅ | No | No |
| Documents | ✅ | No | No |
| Vision / screen | ✅ | No | No |
| PC control | ✅ | No | No |
| Web search | — | Yes | Yes |
| Open web pages | — | Yes | Yes |
| Weather | — | Yes | Yes |
| Translation | — | Yes (fallback) | Yes |
| Spotify control | — | Yes | Yes |
| Discord / Telegram | — | When configured | Yes |
| Mobile / browser extension | LAN | When configured | Peer-to-peer |
| External MCP servers | — | When configured | Yes |

**Approved phrasing:** *"Local features run on your PC. Network-enabled features
communicate externally only when you use or configure them. O.A.S.I.S. is
offline-first, not network-blind."*

**Banned phrasing:** "nothing ever leaves your PC", "sends nothing anywhere",
"completely offline" (as a product-wide claim), "zero network activity".

## 5. Permissions — official model

Source: `registry.py` (`HIGH_IMPACT_TOOLS`, `_default_risk`, `_tool_permissions`).

| Level | Meaning | Examples | Behavior |
|---|---|---|---|
| **Low** | Non-destructive reads | `system_info`, `file_search`, `wifi_info` | Automatic |
| **Medium** | Reversible actions | `write_file`, `clipboard_control`, `open_url` | Allow / Deny / Ask |
| **High** | High-impact actions | `code_agent`, `python_sandbox`, `run_workflow` | Confirmation required |
| **Critical** | Potentially destructive | `system_control`, `kill_process`, `system_cleanup` | Explicit confirmation, every time |

## 6. Models

- Format: **GGUF** (compatible models), run via local runtime.
- Bundled profiles: `gemma-4b-it`, `qwen-2.5-1.5b`, `llama-3.2-3b` (`models_manifest.json`).
- **Do not promise** "any GGUF runs". Say *"supports compatible GGUF models"*.
- No benchmark numbers published unless measured with model, quant, hardware,
  RAM/VRAM, context and date recorded.

## 7. Claim categories

Every public claim must be one of: **VERIFIED** · **QUALIFIED** · **PLANNED** ·
**EXPERIMENTAL** · **ILLUSTRATIVE**. See `CLAIMS_AUDIT.md`.
