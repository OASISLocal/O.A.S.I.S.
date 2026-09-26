# -*- coding: utf-8 -*-
"""Keep the two languages apart.

Two phases:

1. Source. Spanish and English share their layouts, so an href written as
   {{ '/faq.html' | relative_url }} is an English link on the Spanish page. That
   shipped in 59 links across default.html and legal.html before it was caught.

2. Rendered, when _site exists. Walks the built Spanish pages and reports any
   <a href> that leaves /es/. Three things are legitimately allowed to leave:
     - the language switch itself (it has hreflang, and pointing it at the other
       language is the entire point)
     - files with no Spanish twin: /assets/, /llms.txt, the feeds
     - external links
"""
import io, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "_site")

SHARED_OK = re.compile(r"^/(assets/|llms\.txt$|blog/feed\.xml$|blog/rss\.xml$|favicon\.ico$)")
UNPREFIXED = re.compile(r"""href="\{\{\s*['"](\/[^'"]*)['"]\s*\|\s*relative_url""")
LAYOUTS = ["_layouts/default.html", "_layouts/legal.html"]
ANCHOR = re.compile(r'<a\b([^>]*?)href="([^"]+)"([^>]*)>')

problems = []

# ---------- 1. source ----------
for rel in LAYOUTS:
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.isfile(path):
        problems.append("%s: missing" % rel)
        continue
    for n, line in enumerate(io.open(path, encoding="utf-8"), 1):
        for m in UNPREFIXED.finditer(line):
            target = m.group(1)
            if SHARED_OK.match(target):
                continue
            problems.append("%s:%d: %s is not language-aware (use {{ lp | append: %r }})"
                            % (rel, n, target, target))

# ---------- 2. rendered ----------
rendered = 0
if not os.path.isdir(SITE):
    print("check_lang: _site no existe, solo se comprueba el fuente.")
else:
    baseurl = ""
    cfg = io.open(os.path.join(ROOT, "_config.yml"), encoding="utf-8").read()
    m = re.search(r'^baseurl:\s*"?([^"\n]+)"?', cfg, re.M)
    if m:
        baseurl = m.group(1).strip()
    for dp, _dirs, files in os.walk(SITE):
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            url = "/" + os.path.relpath(p, SITE).replace(os.sep, "/")
            if url.endswith("/index.html"):
                url = url[:-len("index.html")]
            if not url.startswith("/es/"):
                continue
            rendered += 1
            h = io.open(p, encoding="utf-8", errors="replace").read()
            for pre, _href, post in ANCHOR.findall(h):
                attrs = pre + post
                if "hreflang" in attrs or "data-lang-switch" in attrs:
                    continue                       # the language switch itself
                if not _href.startswith(baseurl + "/"):
                    continue                       # external, mailto, anchor…
                target = _href[len(baseurl):]
                if target.startswith("/es/") or SHARED_OK.match(target):
                    continue
                problems.append("%s: link %s leaves the Spanish site" % (url, _href))

if problems:
    print("check_lang: %d problema(s):" % len(problems))
    for p in problems[:40]:
        print("  x " + p)
    if len(problems) > 40:
        print("  ... y %d mas" % (len(problems) - 40))
    sys.exit(1)
print("check_lang: OK (fuente: %d layouts; render: %d paginas ES sin fugas)"
      % (len(LAYOUTS), rendered))
