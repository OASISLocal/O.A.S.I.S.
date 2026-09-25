# -*- coding: utf-8 -*-
"""Claim guard for the Journal. Run before every push.

    python check_claims.py

Rules come from PRODUCT_TRUTH.md and _data/journal_terms.json:

  1. forbidden phrasings (the site is offline-first, not network-blind)
  2. "any GGUF runs", "Max is on sale", "the AI understands" ...
  3. a performance figure without a recorded measurement block
  4. Spanish posts must use the agreed glossary renderings
  5. Spanish posts must not contain leftover English section scaffolding
"""
import io, os, re, sys, glob, json

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
RULES = json.load(io.open("_data/journal_terms.json", encoding="utf-8"))
problems = []
notes = []


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def front_matter(src):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", src, re.S)
    if not m:
        return {}
    fm, key = {}, None
    for line in m.group(1).split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and key:
            fm[key] += " " + line.strip()
            continue
        k, _, v = line.partition(":")
        key = k.strip()
        v = v.strip()
        if v.startswith(("'", '"')) and v.endswith(("'", '"')) and len(v) > 1:
            v = v[1:-1]
        fm[key] = v
    return fm


# 1 + 2. forbidden phrasings, and 3. unmeasured performance figures
PERF = re.compile(r"(\d+[\.,]?\d*)\s*(tokens?\s*/\s*s|token/s|tok/s|tokens per second|tokens por segundo|"
                  r"ms de latencia|ms latency|s de respuesta)", re.I)
MEASURE_ANCHORS = [r"how this was measured", r"c[oó]mo se midi[oó]",
                   r"model:", r"quantization:", r"hardware:", r"context"]

posts = sorted(glob.glob("_posts/*.md"))
if not posts:
    print("check_claims.py: OK (no posts yet)")

for f in posts:
    src = read(f)
    fm = front_matter(src)
    name = os.path.basename(f)
    lang = fm.get("lang", "en")
    body = src.split("---", 2)[-1] if src.startswith("---") else src

    for rule in RULES["forbidden"]:
        if lang not in rule["lang"]:
            continue
        for m in re.finditer(rule["pattern"], body, re.I):
            line = body[:m.start()].count("\n") + 1
            problems.append("%s:%d forbidden (%s): %r — %s"
                            % (name, line, rule["id"], m.group(0), rule["why"]))

    # 3. performance numbers need a measurement record
    has_block = any(re.search(a, body, re.I) for a in MEASURE_ANCHORS)
    for m in PERF.finditer(body):
        if not has_block:
            line = body[:m.start()].count("\n") + 1
            problems.append("%s:%d performance figure %r without a 'How this was measured' block "
                            "(model, quantization, hardware, RAM, VRAM, context, date)"
                            % (name, line, m.group(0)))

    # 4. glossary renderings in Spanish posts
    if lang == "es":
        low = body.lower()
        for en, es in RULES["terms"].items():
            if es.lower() in low:
                continue
            # the Spanish rendering should be used instead of a bare English term
            if en in RULES.get("keep_in_english", []):
                continue
            if re.search(r"\b%s\b" % re.escape(en), body, re.I):
                notes.append("%s: uses %r where the glossary says %r" % (name, en, es))
        # 5. leftover English scaffolding in a Spanish post
        for leftover in (r"^#{1,3}\s*(Part|Level|Step)\b", r"\bIn short\b", r"\bRead the first\b"):
            for m in re.finditer(leftover, body, re.I | re.M):
                line = body[:m.start()].count("\n") + 1
                problems.append("%s:%d English scaffolding in a Spanish post: %r"
                                % (name, line, m.group(0)))

for n in notes:
    print("note:", n)
if problems:
    print("\nPROBLEMS (%d):" % len(problems))
    for p in problems:
        print("  x", p)
    sys.exit(1)
print("check_claims.py: OK (%d posts checked)" % len(posts))
