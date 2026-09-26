# -*- coding: utf-8 -*-
"""Generate llms.txt from site-data.json, the dictionaries and the posts.

Why: llms.txt was 34 hand-written lines that had already drifted (it hardcoded
"v0.2.0" and did not mention the Journal or the glossary, which is the part an
answer engine would actually cite). Everything version-shaped now comes from
site-data.json, and the parts that grow with the site grow here automatically.

llms.txt is not a ranking mechanism; it is a map. Its value is that an answer
engine can find the plain-language explanation instead of the product page.

    python build_llms.py            # write llms.txt
    python build_llms.py --check    # fail if stale (run by sync-web.ps1)
"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.abspath(__file__))
from site_config import SITE

DATA = os.path.join(ROOT, "site-data.json")

# Prose that does not change with a release. Written here rather than in
# site-data.json because it is editorial copy, not data.
INTRO = ("O.A.S.I.S. runs compatible GGUF models locally and adds chat, voice, "
         "memory, documents, everyday PC tools and explicit permissions. The "
         "Personal edition is free and does not require an account. The "
         "application is proprietary; this public repository contains releases, "
         "documentation and transparency material, not application source code.")

NETWORK = ("Local features run on your PC. Network-enabled features communicate "
           "externally only when you use or configure them. O.A.S.I.S. is "
           "offline-first, not network-blind. Web search, online pages, weather, "
           "translation fallbacks, messaging, companions and external MCP servers "
           "can require network access.")

MODELS = ("Compatible GGUF models are supported. Bundled profiles include "
          "`gemma-4b-it`, `qwen-2.5-1.5b` and `llama-3.2-3b`. Compatibility "
          "depends on model, quantization, context size, backend and hardware.")

SERIES_NAMES = {"foundations": "Foundations"}


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def posts():
    """Published posts, EN only, in reading order. The ES twin is listed as a
    separate link because an answer engine may be asked in either language."""
    out = []
    folder = os.path.join(ROOT, "_posts")
    for name in sorted(os.listdir(folder)):
        if not name.endswith((".md", ".markdown")):
            continue
        src = io.open(os.path.join(folder, name), encoding="utf-8").read()
        head = src.split("---", 2)[1] if src.startswith("---") else src

        def field(key):
            m = re.search(r'^%s:\s*"?(.*?)"?\s*$' % key, head, re.M)
            return m.group(1).strip() if m else None

        if field("sitemap") == "false":
            continue                       # the components demo is not content
        lang = field("lang") or "en"
        if lang != "en":
            continue
        perm = field("permalink")
        stem = name.rsplit(".", 1)[0]
        slug = stem[11:]
        url = (SITE + perm) if perm else "%s/blog/%s/%s/%s/%s/" % (
            SITE, stem[0:4], stem[5:7], stem[8:10], slug)
        order = int(field("order") or 0)
        out.append({"title": field("title"), "excerpt": field("excerpt"),
                    "url": url, "series": field("series"), "order": order,
                    "minutes": field("reading_minutes"),
                    "ref": field("ref")})
    out.sort(key=lambda p: (p["order"] or 99, p["title"] or ""))
    return out


def es_twin(ref):
    """The Spanish URL of an article, read from its own front matter."""
    folder = os.path.join(ROOT, "_posts")
    for name in sorted(os.listdir(folder)):
        if not name.endswith((".md", ".markdown")):
            continue
        src = io.open(os.path.join(folder, name), encoding="utf-8").read()
        head = src.split("---", 2)[1] if src.startswith("---") else src
        m = re.search(r'^ref:\s*"?([^"\n]+?)"?\s*$', head, re.M)
        if not m or m.group(1).strip() != ref:
            continue
        if not re.search(r'^lang:\s*"?es"?\s*$', head, re.M):
            continue
        perm = re.search(r'^permalink:\s*"?([^"\n]+?)"?\s*$', head, re.M)
        if perm:
            return SITE + perm.group(1).strip()
    return None


def build():
    d = load(DATA)
    version = d["version"]
    status = d.get("status", "")
    platform = " / ".join(d.get("platform", []))
    tools = d.get("tools", "")
    road = d.get("roadmap", {})

    L = []
    L.append("# O.A.S.I.S.")
    L.append("")
    tagline = "Local-first AI assistant for Windows %s x64." % platform.replace("Windows ", "")
    L.append("> %s Public %s v%s." % (tagline, status, version))
    L.append("")
    L.append("## Product")
    L.append("")
    L.append(INTRO)
    L.append("")
    L.append("## Capabilities")
    L.append("")
    for item in road.get("now", []):
        L.append("- %s" % item)
    personal = d.get("personal", {})
    if personal.get("limits"):
        L.append("- %s" % personal["limits"])
    if personal.get("tool_note"):
        L.append("- %s" % personal["tool_note"])
    if d.get("max_only"):
        # The honest half: what the free edition does not include. Losing this
        # line is how a generated file ends up more flattering than the site.
        L.append("- Max-only or planned: %s" % ", ".join(d["max_only"]))
    L.append("")
    L.append("## Network model")
    L.append("")
    L.append(NETWORK)
    L.append("")
    L.append("## Models")
    L.append("")
    L.append(MODELS)
    L.append("")

    arts = posts()
    if arts:
        L.append("## Journal")
        L.append("")
        L.append("Plain-language explanations, written for someone deciding "
                 "whether a local assistant is real. Each one is a complete "
                 "answer rather than a summary, and they exist in Spanish too.")
        L.append("")
        for a in arts:
            mins = " (%s min read)" % a["minutes"] if a["minutes"] else ""
            L.append("- [%s](%s): %s%s" % (a["title"], a["url"], a["excerpt"], mins))
            es = es_twin(a["ref"]) if a["ref"] else None
            if es:
                L.append("  - [Español](%s)" % es)
        L.append("- [Journal index](%s/blog/)" % SITE)
        L.append("")

    tips = load(os.path.join(ROOT, "tooltips.json"))
    n_terms = len([k for k in tips if not k.startswith("_")])
    L.append("## Glossary")
    L.append("")
    L.append("%d terms defined in plain language, with a Spanish rendering for "
             "each. The same text appears as a tooltip on the pages that use it, "
             "so a definition is never longer than the page it sits on." % n_terms)
    L.append("")
    L.append("- [Glossary](%s/glossary/)" % SITE)
    L.append("- [Glosario](%s/es/glossary/)" % SITE)
    L.append("")

    if road.get("next"):
        L.append("## Roadmap")
        L.append("")
        L.append("Next, in order: %s." % ", ".join(road["next"]))
        L.append("")

    L.append("## Official links")
    L.append("")
    L.append("- Website: %s/" % SITE)
    L.append("- Spanish website: %s/es/" % SITE)
    L.append("- Journal: %s/blog/" % SITE)
    L.append("- Releases: https://github.com/OASISLocal/O.A.S.I.S./releases")
    L.append("- Documentation: https://github.com/OASISLocal/O.A.S.I.S./tree/main/docs")
    L.append("- Issues: https://github.com/OASISLocal/O.A.S.I.S./issues")
    L.append("- Privacy model: %s/privacy.html" % SITE)
    L.append("- llms.txt: %s/llms.txt" % SITE)
    L.append("")
    return "\n".join(L), version, len(arts), n_terms


def main():
    text, version, n_arts, n_terms = build()

    # Item 22 of the search plan: one source of truth for the version. The
    # product pages are static HTML with no front matter, so they cannot read
    # site-data.json; this makes the data file authoritative and fails the build
    # if a page disagrees, instead of leaving it correct by luck.
    stale = []
    for folder in ("", "es"):
        d = os.path.join(ROOT, folder) if folder else ROOT
        for name in sorted(os.listdir(d)):
            if not name.endswith(".html") or name == "404.html":
                continue
            h = io.open(os.path.join(d, name), encoding="utf-8", errors="replace").read()
            for m in re.finditer(r"v?(0\.\d+\.\d+)", h):
                if m.group(1) != version:
                    stale.append("%s/%s shows v%s but site-data.json says v%s"
                                 % (folder or ".", name, m.group(1), version))
    problems = []
    if stale:
        problems += sorted(set(stale))[:10]
    if "--check" in sys.argv:
        path = os.path.join(ROOT, "llms.txt")
        have = io.open(path, encoding="utf-8").read() if os.path.isfile(path) else ""
        if have.replace("\r\n", "\n") != text.replace("\r\n", "\n"):
            problems.append("llms.txt is stale (run: python build_llms.py)")
    if problems:
        print("build_llms: %d problem(s):" % len(problems))
        for p in problems:
            print("  x " + p)
        return 1
    if "--check" in sys.argv:
        print("build_llms --check: OK (llms.txt al dia, version v%s coherente en %d paginas)"
              % (version, 2 * len([f for f in os.listdir(ROOT) if f.endswith(".html")])))
        return 0
    with io.open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote llms.txt (%d bytes, v%s, %d articulos, %d terminos)"
          % (len(text.encode("utf-8")), version, n_arts, n_terms))
    return 0


if __name__ == "__main__":
    sys.exit(main())
