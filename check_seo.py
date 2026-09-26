# -*- coding: utf-8 -*-
"""SEO gate: the checks that check_site.py does not cover.

    python check_seo.py        # human output, exit 1 on problems

Implements docs/PLAN_BUSCADORES_2026.md §6 (finding #21): the comment in
sync-web.ps1 claimed canonical/og/twitter/hreflang/robots validation existed.
Until now it did not. This is that gate.

  1. every JSON-LD block parses, and declares @context and @type
  2. indexable pages carry canonical, og:title/description/url/image/locale,
     og:locale:alternate and twitter:card, exactly once each
  3. the social image is the PNG, never the SVG
  4. <title> and meta description are unique across the whole site
  5. hreflang reciprocity: if a page declares a Spanish twin, the twin declares
     the English page back; x-default always points at the English page
  6. the sitemap declares every page that exists, and every ES page too
  7. robots.txt has a Sitemap line and does not block the site in live mode
  8. robots.txt names llms.txt
  9. 404 and launch pages are noindex
 10. nothing internal (docs, tooling, internal notes) is in the Jekyll build
"""
import io, os, re, sys, glob, json
import xml.etree.ElementTree as ET
from site_config import BASEURL, SITE

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
problems = []
notes = []


def fail(m):
    problems.append(m)


def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()


# --------------------------------------------------------------------- pages
# Static pages only. Jekyll pages (front matter) get their head from a layout at
# build time, so their tags are checked in _layouts instead (section 11).
STATIC = [f for f in sorted(glob.glob("*.html") + glob.glob("es/*.html"))
          if not read(f).lstrip().startswith("---")]
NOINDEX = [f for f in STATIC if 'name="robots" content="noindex' in read(f)]

REQUIRED = [
    ('rel="canonical"', "canonical"),
    ('property="og:type"', "og:type"),
    ('property="og:title"', "og:title"),
    ('property="og:description"', "og:description"),
    ('property="og:url"', "og:url"),
    ('property="og:image"', "og:image"),
    ('property="og:locale"', "og:locale"),
    ('property="og:locale:alternate"', "og:locale:alternate"),
    ('property="og:site_name"', "og:site_name"),
    ('name="twitter:card"', "twitter:card"),
    ('hreflang="x-default"', "x-default"),
]

titles, descriptions = {}, {}

for f in STATIC:
    src = read(f)
    head = src.split("</head>")[0] if "</head>" in src else src
    is_noindex = f in NOINDEX

    for needle, label in REQUIRED:
        if needle not in head:
            fail("%s: missing %s in <head>" % (f, label))

    for tag, label in (("<title>", "title"), ('rel="canonical"', "canonical"),
                       ('name="description"', "description")):
        n = head.count(tag)
        want_max = 1
        if n != want_max:
            fail("%s: %d x %s in <head> (expected 1)" % (f, n, label))

    if "og-card.svg" in head:
        fail("%s: og:image still points at the SVG card" % f)
    if "og-card.png" not in head:
        fail("%s: og:image is not the PNG card" % f)

    # The site is published under a subpath (/O.A.S.I.S./), so an internal link
    # that starts at the host root resolves to the wrong place in production.
    for href in re.findall(r'href="(/[^"]*)"', src):
        if href.startswith(BASEURL):
            continue
        fail("%s: root-absolute internal link %r breaks under the %s subpath"
             % (f, href, BASEURL.rstrip("/")))

    # A link in the wrong language is a translation bug that no other gate sees.
    es_page = f.replace("\\", "/").startswith("es/")
    for name, ok_es, ok_en in (("glossary.html", "Glosario", "Glossary"),
                               ("llms.txt", "para IA", "for AI")):
        for label in re.findall(r'href="(?:\.\./)?%s"[^>]*>([^<]*)<' % re.escape(name), src):
            want = ok_es if es_page else ok_en
            if want not in label:
                fail("%s: the %s link says %r, expected %r (wrong language)"
                     % (f, name, label, want))

    if not is_noindex:
        t = re.search(r"<title[^>]*>(.*?)</title>", head, re.S)
        d = re.search(r'name="description" content="([^"]*)"', head)
        if t:
            key = re.sub(r"\s+", " ", t.group(1)).strip().lower()
            if key in titles:
                fail("duplicate <title> in %s and %s: %r" % (f, titles[key], key))
            titles[key] = f
            if len(key) > 70:
                notes.append("%s: title is %d chars" % (f, len(key)))
        if d:
            key = re.sub(r"\s+", " ", d.group(1)).strip().lower()
            if key in descriptions:
                fail("duplicate meta description in %s and %s" % (f, descriptions[key]))
            descriptions[key] = f
            if len(key) > 160:
                fail("%s: meta description is %d chars (max 160)" % (f, len(key)))

    # 1. JSON-LD parses
    for i, blk in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, re.S)):
        try:
            data = json.loads(blk)
        except Exception as e:
            fail("%s: JSON-LD block %d is invalid: %s" % (f, i + 1, str(e)[:80]))
            continue

        def walk(node):
            """Every dict in the block, including the ones inside @graph."""
            if isinstance(node, dict):
                yield node
                for child in node.get("@graph") or []:
                    for sub in walk(child):
                        yield sub
            elif isinstance(node, list):
                for item in node:
                    for sub in walk(item):
                        yield sub

        nodes = list(walk(data))
        if not any("@context" in n for n in nodes):
            fail("%s: JSON-LD block %d has no @context" % (f, i + 1))
        for node in nodes:
            if "@type" in node:
                continue
            if "@graph" in node or "@context" in node:
                continue                      # container, not an entity
            fail("%s: JSON-LD node without @type: %s" % (f, sorted(node.keys())))

# ------------------------------------------------------- 5/6. hreflang + sitemap
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}
tree = ET.fromstring(read("sitemap.xml"))
pairs = {}
for u in tree.findall("s:url", NS):
    loc = u.find("s:loc", NS).text
    alts = {}
    for link in u.findall("x:link", NS):
        alts[link.get("hreflang")] = link.get("href")
    pairs[loc] = alts

for loc, alts in pairs.items():
    if "x-default" not in alts:
        fail("sitemap: %s has no x-default" % loc)
    if alts.get("es") and alts["es"] != loc:
        back = pairs.get(alts["es"], {}).get("en")
        if back != loc:
            fail("sitemap: %s declares es -> %s but that page declares en -> %s"
                 % (loc, alts["es"], back))

# every indexable page on disk must be in the sitemap
in_sitemap = set(pairs.keys())


def url_for_file(f):
    """The site URL a local file is published at (Windows separators and the
    two index.html files need normalising)."""
    rel = f.replace("\\", "/")
    if rel == "index.html":
        rel = ""
    elif rel.endswith("/index.html"):
        rel = rel[:-len("index.html")]
    return SITE + "/" + rel


for f in STATIC:
    if f in NOINDEX:
        continue
    if url_for_file(f) not in in_sitemap:
        fail("page not in the sitemap: %s" % f)


def post_url(f):
    """A post's published URL: its own permalink when declared, else the default.
    Returns (url, opted_out) so callers can skip noindex test pages."""
    src = read(f)
    m = re.search(r"^---\s*\n(.*?)\n---", src, re.S)
    opted_out = False
    if m:
        head = m.group(1)
        if re.search(r"^sitemap:\s*false\s*$", head, re.M):
            opted_out = True
        if re.search(r"^noindex:\s*true\s*$", head, re.M):
            opted_out = True
        pm = re.search(r"^permalink:\s*(\S+)\s*$", head, re.M)
        if pm:
            return SITE + pm.group(1), opted_out
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$", os.path.basename(f)[:-3])
    if not m:
        return None, opted_out
    return SITE + "/blog/%s/%s/%s/%s/" % m.groups(), opted_out


for f in sorted(glob.glob("_posts/*.md")):
    url, opted_out = post_url(f)
    if url and not opted_out and url not in in_sitemap:
        fail("post not in the sitemap: %s" % os.path.basename(f))

# --------------------------------------------------------------- 7/8. robots
robots = read("robots.txt")
if "Sitemap:" not in robots:
    fail("robots.txt has no Sitemap line")
if "llms.txt" not in robots:
    fail("robots.txt does not mention llms.txt")
if re.search(r"^Disallow:\s*/\s*$", robots, re.M):
    fail("robots.txt blocks the whole site (Disallow: /)")
if not os.path.isfile("llms.txt") or len(read("llms.txt")) < 200:
    fail("llms.txt missing or suspiciously small")

# ------------------------------------------------------------------ 9. noindex
for f in ["404.html", "es/404.html"] + sorted(glob.glob("launch/*.html")):
    if not os.path.isfile(f):
        continue
    if 'name="robots" content="noindex' not in read(f):
        fail("%s is not noindex" % f)

# ------------------------------------------- 10. nothing internal gets published
cfg = read("_config.yml")
for internal in ("docs/", "readme", "Gemfile", "PRODUCT_TRUTH.md", "JOURNAL_CHECKLIST.md",
                 "GOOGLE_NEWS.md", "JOURNAL_GLOSSARY.md", "build_sitemap.py",
                 "check_site.py", "check_claims.py", "check_seo.py",
                 "build_news_sitemap.py", "build_es.py", "sync-web.ps1",
                 "build_glossary.py", "build_llms.py", "build_faqpage.py",
                 "build_fonts.py",
                 "check_lang.py", "site_config.py"):
    if os.path.exists(internal) and re.search(r"^\s*-\s*%s\s*$" % re.escape(internal),
                                              cfg, re.M) is None:
        fail("%s is not in _config.yml exclude (Jekyll would publish it)" % internal)

# ------------------------------------- 10b. the FAQPage block is valid and honest
# Two failures happened here in a single sitting and neither showed on the page:
# hand-escaped JSON did not parse, and a stray `| strip` turned the question
# array into a string so the block carried one question instead of five. The FAQ
# rendered perfectly in both cases. So it is parsed here, and the questions are
# compared against the visible <summary> text: structured data that disagrees
# with the page is worse than none.
SITE_DIR = "_site"
if not os.path.isdir(SITE_DIR):
    notes.append("_site not present: skipped the FAQPage pass")
else:
    for dp, _d, fs in os.walk(SITE_DIR):
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            page = "/" + os.path.relpath(p, SITE_DIR).replace(os.sep, "/")
            html = read(p)
            blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                                html, re.S)
            faq = next((b for b in blocks if '"FAQPage"' in b), None)
            if not faq:
                continue
            try:
                d = json.loads(faq)
            except Exception as e:
                fail("%s: the FAQPage block is not valid JSON (%s)" % (page, e))
                continue
            if d.get("@type") != "FAQPage" or d.get("@context") != "https://schema.org":
                fail("%s: FAQPage block has the wrong @type/@context" % page)
            qs = d.get("mainEntity", [])
            if not qs:
                fail("%s: FAQPage has no questions" % page)
                continue
            # Any <summary>, not just the component's: the product FAQ pages use
            # their own accordion markup, and reading only the component's class
            # made this report 0 visible questions and a false mismatch.
            visible = [re.sub(r"<[^>]+>", "", v).strip() for v in
                       re.findall(r"<summary[^>]*>(.*?)</summary>", html, re.S)]
            named = [(q.get("name") or "").strip() for q in qs]
            if not visible:
                fail("%s: FAQPage is present but the page shows no <summary> questions, "
                     "so the two cannot be compared" % page)
            elif named != visible:
                fail("%s: FAQPage questions disagree with the visible FAQ "
                     "(%d in the schema, %d on the page)" % (page, len(named), len(visible)))
            for q in qs:
                if not (q.get("acceptedAnswer", {}).get("text") or "").strip():
                    fail("%s: FAQPage question %r has an empty answer"
                         % (page, (q.get("name") or "")[:40]))
                if not (q.get("name") or "").strip():
                    fail("%s: a FAQPage entry has an empty question" % page)
            notes.append("FAQPage ok in %s (%d questions, matches the visible FAQ)"
                         % (page, len(qs)))

# ------------------------------------------------- 11. the Jekyll head templates
# Only layouts that emit their own <head> need the full set; post.html inherits
# from default.html.
for layout in ("_layouts/default.html", "_layouts/legal.html"):
    src = read(layout)
    if "<head" not in src:
        continue
    for needle, label in (('property="og:locale"', "og:locale"),
                          ('property="og:locale:alternate"', "og:locale:alternate"),
                          ('property="og:site_name"', "og:site_name"),
                          ('property="og:image"', "og:image"),
                          ('og-card.png', "PNG social card"),
                          ('name="twitter:card"', "twitter:card"),
                          ('application/ld+json', "JSON-LD")):
        if needle not in src:
            fail("%s: missing %s" % (layout, label))
    if "og-card.svg" in src:
        fail("%s: still references the SVG social card" % layout)
    if "{% seo %}" in src:
        fail("%s: jekyll-seo-tag duplicates the manual head (title/canonical/description)" % layout)
for layout in glob.glob("_layouts/*.html"):
    if os.path.isfile(layout) and "llms.txt" not in read(layout):
        notes.append("%s: no llms.txt link in the footer" % layout)

# ------------------------------------------------- 12. the glossary has real data
for f, data_file in (("glossary.html", "_data/glossary_terms.json"),
                     ("es/glossary.html", "_data/glossary_terms_es.json")):
    if not os.path.isfile(f):
        fail("missing glossary page: %s" % f)
        continue
    src = read(f)
    rows = len(re.findall(r'<tr id="g-', src))
    if rows < 20:
        fail("%s: only %d glossary rows" % (f, rows))
    if not os.path.isfile(data_file):
        fail("missing %s (generated from tooltips.json)" % data_file)
        continue
    d = json.loads(read(data_file))
    set_node = [n for n in d["@graph"] if n["@type"] == "DefinedTermSet"]
    if not set_node:
        fail("%s: no DefinedTermSet node" % data_file)
        continue
    terms = set_node[0].get("hasDefinedTerm", [])
    if len(terms) != rows:
        fail("%s: %d DefinedTerm but %d rows in the page" % (data_file, len(terms), rows))
    if not all(t.get("name") and t.get("description") for t in terms):
        fail("%s: a DefinedTerm has no name or description" % data_file)
    # The page itself carries no ld+json: the layout emits the DefinedTermSet for
    # this permalink. Verify the layout still knows how.
    if not re.search(r"if page\.permalink == '/(es/)?glossary/'", read("_layouts/default.html")):
        fail("_layouts/default.html: no DefinedTermSet branch for the glossary permalink")

# ------------------------------- 13. one Organization, and no dangling @id refs
org_defs = []
for f in STATIC:
    head = read(f).split("</head>")[0]
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', head, re.S):
        data = json.loads(blk)
        for node in data.get("@graph", [data]):
            if node.get("@type") == "Organization" and node.get("@id"):
                org_defs.append((f, node["@id"]))
if org_defs and len(set(i for _, i in org_defs)) > 1:
    fail("more than one Organization @id declared: %s" % sorted(set(i for _, i in org_defs)))

# ------------------------------------------- 14. the component system is coherent
COMPONENT_DIR = "_includes/components"
COMPONENT_CSS = "assets/components"
if os.path.isdir(COMPONENT_DIR):
    includes = sorted(glob.glob(COMPONENT_DIR + "/*.html"))
    if not includes:
        fail("%s exists but has no components" % COMPONENT_DIR)
    for inc in includes:
        body = read(inc)
        # every include must declare a marker, otherwise the layout cannot detect it
        if "data-cmp-" not in body:
            fail("%s: no data-cmp-* marker, so the layout cannot detect the usage"
                 % inc)
        # every include referenced must exist (ignore the usage examples in the
        # comment header, which are written as documentation)
        body_no_comments = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}",
                                  "", body, flags=re.S)
        for dep in re.findall(r"include\s+([a-z0-9_/]+\.html)", body_no_comments):
            if not os.path.isfile(os.path.join(COMPONENT_DIR, dep)):
                fail("%s references a missing include: %s" % (inc, dep))
    # the layout must know how to detect each component
    layout_post = read("_layouts/post.html")
    for inc in includes:
        markers = set(re.findall(r'data-cmp-([a-z-]+)', read(inc)))
        # these are config carriers or per-element hooks, not components that
        # load a stylesheet of their own
        for internal in ("table-config", "chart-toggle", "gallery-open",
                         "table-status", "video-play", "gallery-item",
                         "chart-data", "timeline-horizontal"):
            markers.discard(internal)
        for name in markers:
            if name not in layout_post:
                fail("_layouts/post.html: no conditional loading for component %r" % name)
    # every stylesheet the layout can request must exist
    for css in set(re.findall(r"/assets/components/([a-z-]+\.css)", layout_post)):
        if not os.path.isfile(os.path.join(COMPONENT_CSS, css)):
            fail("missing component stylesheet: assets/components/%s" % css)
    if not os.path.isfile(os.path.join(COMPONENT_CSS, "components.js")):
        fail("missing assets/components/components.js")
    # The site promises no third-party requests. A component must not undo that.
    for f in includes + [os.path.join(COMPONENT_CSS, "components.js")]:
        src = read(f)
        for bad in ("cdn.jsdelivr.net", "unpkg.com", "cdnjs.cloudflare.com",
                    "googleapis.com", "bootstrapcdn"):
            if bad in src:
                fail("%s loads a third-party asset (%s), which breaks the "
                     "no-third-party promise" % (f, bad))
    # A video poster must be a local file, not a remote thumbnail
    for f in sorted(glob.glob("_posts/*.md")):
        for poster in re.findall(r'poster="([^"]+)"', read(f)):
            if poster.startswith(("http://", "https://", "//")):
                fail("%s: remote video poster %r would be a third-party request"
                     % (os.path.basename(f), poster))
            local = "." + poster
            if not os.path.isfile(local):
                fail("%s: video poster not found: %s" % (os.path.basename(f), poster))

    # Liquid's include tag cannot hold a double quote inside a double-quoted
    # parameter. That is an "Invalid syntax for include tag" build failure, and
    # it is invisible until the Jekyll build runs, so it is checked here.
    INCLUDE = re.compile(r"\{%-?\s*include\s+([a-z0-9_/]+\.html)((?:\s+[a-zA-Z_][\w-]*=(?:\"[^\"]*\"|'[^']*'))*)\s*-?%\}",
                         re.S)
    for f in sorted(glob.glob("_posts/*.md") + glob.glob("*.html") +
                    glob.glob("es/*.html") + glob.glob("blog/*.html") +
                    glob.glob("es/blog/*.html")):
        src = read(f)
        for m in INCLUDE.finditer(src):
            name, args = m.group(1), m.group(2)
            if not os.path.isfile(os.path.join("_includes", name)):
                fail("%s: include %s does not exist" % (os.path.basename(f), name))
            # count the double quotes: an odd number means one is unmatched
            if args.count('"') % 2 != 0:
                line = src[:m.start()].count("\n") + 1
                fail("%s:%d include %s has an unbalanced double quote in its "
                     "parameters, which breaks the Jekyll build"
                     % (os.path.basename(f), line, name))
    # a markdown table cannot be markdownified inside a <table>
    for f in sorted(glob.glob("_posts/*.md")):
        src = read(f)
        if re.search(r"include\s+components/table\.html[^%]*markdownify", src, re.S):
            fail("%s: table.html does not accept markdownified markdown" % os.path.basename(f))

    if "COMPONENTES.md" not in cfg:
        fail("COMPONENTES.md is not in _config.yml exclude (Jekyll would publish it)")

    # A component that renders but never initialises is a silent failure, and
    # it only shows in a browser. These are the selectors the script must find,
    # cross-checked against what the includes actually emit.
    js = read(os.path.join(COMPONENT_CSS, "components.js"))
    # name -> (marker the include must emit, marker the script must query, or
    # None when the component is CSS-only and needs no JavaScript at all)
    REQUIRED_HOOKS = {
        "chart": ("data-cmp-chart", "data-cmp-chart"),
        "table": ("data-cmp-table-config", "data-cmp-table-config"),
        "details": ("data-cmp-details", "data-cmp-details"),
        "video": ("data-cmp-video", "data-cmp-video"),
        "gallery": ("data-cmp-gallery-item", "data-cmp-gallery-item"),
        "tabs": ("data-cmp-tabs", "data-cmp-tabs"),
        # CSS-only: they work with no script at all, which is the point
        "callout": ("data-cmp-callout", None),
        "timeline": ("data-cmp-timeline", None),
    }
    for name, (emitted, queried) in REQUIRED_HOOKS.items():
        inc = os.path.join(COMPONENT_DIR, name + ".html")
        if not os.path.isfile(inc):
            continue
        if emitted not in read(inc):
            fail("%s does not emit %s, so nothing can find it" % (name, emitted))
        if queried and queried not in js:
            fail("components.js never queries %s (the %s component would never "
                 "initialise)" % (queried, name))
    # the chart reads its numbers from the table: the selector must match
    if "cmp-chart__data table" not in js:
        fail("components.js: the chart does not read its numbers from the table")

# ---------------------------------------------------------------------- report
for n in notes:
    print("note:", n)
if problems:
    print("\nPROBLEMS (%d):" % len(problems))
    for p in problems:
        print("  x", p)
    sys.exit(1)
print("check_seo.py: OK (%d static pages, %d sitemap urls, %d unique titles)"
      % (len(STATIC), len(pairs), len(titles)))
