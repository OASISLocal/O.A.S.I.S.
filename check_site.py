# -*- coding: utf-8 -*-
"""Integrity checks for the site and the Journal. Run before every push.

    python check_site.py        # human output, exit 1 on problems

Checks
  1. every internal href resolves to a file that exists
  2. every hreflang target and every sitemap URL resolves
  3. sitemap.xml is what build_sitemap.py would generate
  4. every Journal post has: excerpt <= 160 chars, >= 3 internal links,
     an EN/ES pair through `ref`, valid JSON-LD expectations, a `lang`
  5. every page referenced by the sitemap exists (and vice versa)
  6. tooling and docs stay excluded from the Jekyll build
  7. the social card PNG exists
"""
import io, os, re, sys, glob, json
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
SITE = "https://oasislocal.github.io/O.A.S.I.S."
problems = []
notes = []


def fail(msg):
    problems.append(msg)


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def post_url_map():
    """Map each Journal post's *built* URL to its source file.

    A post lives in _posts/2026-09-25-slug.md but is published at
    /blog/2026/09/25/slug/ (or at its own permalink for the Spanish twin), so
    the sitemap and the hreflang alternates point at URLs that only exist after
    the Jekyll build. This is how a post is recognised as "real".
    """
    out = {}
    for f in sorted(glob.glob("_posts/*.md")):
        src = read(f)
        fm = front_matter_of(src)
        name = os.path.basename(f)[:-3]
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$", name)
        if not m:
            continue
        perm = fm.get("permalink") or "/blog/%s/%s/%s/%s/" % m.groups()
        out[perm.rstrip("/") + "/"] = f
        out[perm.rstrip("/")] = f
    return out


_POST_URLS = None


def built_post_url(path):
    global _POST_URLS
    if _POST_URLS is None:
        _POST_URLS = post_url_map()
    key = path.split("#")[0].split("?")[0]
    return _POST_URLS.get(key) or _POST_URLS.get(key.rstrip("/") + "/")


def front_matter_of(src):
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


def exists(path):
    """Map a site-absolute path to a local file, or None."""
    p = path.split("#")[0].split("?")[0]
    if not p or p == "/":
        return "index.html"
    if p.endswith("/"):
        rel = p.strip("/").replace("/", os.sep)
        # A permalink served from a page file: /glossary/ <- glossary.html
        flat = rel + ".html"
        if os.path.isfile(flat):
            return flat
        for cand in (os.path.join(".", rel, "index.html"),
                     os.path.join(".", rel, "Index.html")):
            if os.path.isfile(cand):
                return cand
        return built_post_url(p)
    if p.endswith(".xml") or p.endswith(".json") or p.endswith(".txt") or p.endswith(".xsl"):
        return "." + p
    if os.path.isfile("." + p):
        return "." + p
    if os.path.isfile("./" + p.strip("/")):
        return "./" + p.strip("/")
    return built_post_url(p)


# ---------------------------------------------------------------- 1. links
SKIP_EXT = (".ico", ".svg", ".png", ".woff2", ".css", ".js", ".webmanifest")
LINK_FILES = sorted(glob.glob("*.html") + glob.glob("es/*.html") +
                    glob.glob("blog/*.html") + glob.glob("es/blog/*.html") +
                    ["_layouts/default.html", "_layouts/post.html", "_layouts/legal.html"])
for f in LINK_FILES:
    src = read(f)
    base = os.path.dirname(f)
    for href in re.findall(r'href="([^"]+)"', src):
        if href.startswith(("http://", "https://", "mailto:", "#", "data:", "javascript:")):
            continue
        if href.endswith(SKIP_EXT):
            continue
        # relative to the file
        target = os.path.normpath(os.path.join(base, href.split("#")[0].split("?")[0]))
        target = os.path.normpath(target).replace("\\", "/")
        if target.startswith("./"):
            target = target[2:]
        if not target or os.path.isdir(target):
            continue
        # leave Liquid placeholders and assets alone
        if "{" in target or "assets/" in target or "launch/" in target or "i18n/" in target:
            continue
        if not os.path.exists(target):
            fail("broken link in %s -> %s" % (f, href))

# -------------------------------------------------------- 2/5. hreflang+sitemap
sitemap = read("sitemap.xml")
tree = ET.fromstring(sitemap)
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9",
      "x": "http://www.w3.org/1999/xhtml"}
sitemap_locs = [u.find("s:loc", NS).text for u in tree.findall("s:url", NS)]
for loc in sitemap_locs:
    if not exists(loc.replace(SITE, "")):
        fail("sitemap URL with no local file: %s" % loc)
for u in tree.findall("s:url", NS):
    for link in u.findall("x:link", NS):
        href = link.get("href")
        if not exists(href.replace(SITE, "")):
            fail("hreflang target with no local file: %s" % href)

# English pages that exist but are not in the sitemap. The Spanish mirror is
# intentionally not listed as its own <url>: it is reachable through the
# hreflang alternates of each English page (plus the /es/blog/ entry).
IN_SITEMAP = set(loc.replace(SITE, "") for loc in sitemap_locs)
EXPECTED_MISSING = {"/404.html", "/blog/feed.xml",
                    "/blog/feed.xsl", "/blog/posts.json", "/sitemap.xml",
                    "/robots.txt", "/llms.txt", "/site-data.json", "/launch.json"}
for f in glob.glob("*.html"):
    p = "/" + f
    if p == "/index.html":
        p = "/"
    elif f == "glossary.html":
        # Published at the bare permalink /glossary/ (front matter permalink),
        # not at /glossary.html.
        p = "/glossary/"
    if p not in IN_SITEMAP and p not in EXPECTED_MISSING:
        notes.append("page not listed in sitemap: %s" % p)

# ---------------------------------------------------- 3. sitemap is generated
try:
    import build_sitemap
    if build_sitemap.build() != sitemap:
        fail("sitemap.xml does not match build_sitemap.py output (run: python build_sitemap.py)")
    else:
        notes.append("sitemap matches build_sitemap.py (%d urls)" % len(sitemap_locs))
except Exception as e:
    fail("build_sitemap.py could not be run: %s" % e)

# ------------------------------------------------- 1b. links inside the posts
# Markdown links ([text](/path/)) and tooltip data-term keys, which the plain
# href scan above cannot see.
TOOLTIP_KEYS = set(json.loads(read("tooltips.json")).keys()) if os.path.isfile("tooltips.json") else set()
for f in sorted(glob.glob("_posts/*.md")):
    src = read(f)
    body = src.split("---", 2)[-1] if src.startswith("---") else src
    for m in re.finditer(r"\]\((/[^)\s]+)\)", body):
        target = exists(m.group(1))
        if target is None:
            fail("broken link in %s -> %s" % (os.path.basename(f), m.group(1)))
    for term in re.findall(r'data-term="([^"]+)"', body):
        if TOOLTIP_KEYS and term not in TOOLTIP_KEYS:
            fail("%s: data-term %r is not in tooltips.json (the tooltip would never show)"
                 % (os.path.basename(f), term))

# ------------------------------------------------------------- 4. blog posts
def front_matter(path):
    src = read(path)
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", src, re.S)
    if not m:
        return {}, src
    fm = {}
    key = None
    for line in m.group(1).split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and key:      # folded continuation
            fm[key] += " " + line.strip()
            continue
        k, _, v = line.partition(":")
        key = k.strip()
        v = v.strip()
        if v.startswith(("'", '"')) and v.endswith(("'", '"')) and len(v) > 1:
            v = v[1:-1]
        fm[key] = v
    return fm, src

posts = {}
for f in sorted(glob.glob("_posts/*.md")):
    fm, src = front_matter(f)
    lang = fm.get("lang", "en")
    ref = fm.get("ref")
    name = os.path.basename(f)
    if not ref:
        fail("%s: missing `ref` (needed to pair EN and ES)" % name)
        ref = name
    slug = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", name[:-3])
    if not slug:
        fail("%s: filename must start with YYYY-MM-DD-" % name)
    excerpt = fm.get("excerpt", "")
    if not excerpt:
        fail("%s: missing `excerpt` (it is the meta description and the index listing)" % name)
    elif len(excerpt) > 160:
        fail("%s: excerpt is %d chars, max 160" % (name, len(excerpt)))
    if not fm.get("title"):
        fail("%s: missing `title`" % name)
    if len(fm.get("title", "")) > 45:
        notes.append("%s: title is %d chars (>45 makes the full <title> long)" % (name, len(fm["title"])))
    if not fm.get("tags"):
        notes.append("%s: no tags" % name)

    body = src.split("---", 2)[-1] if src.startswith("---") else src
    # internal links, in markdown ([text](/path)), in html (href="/path") and in
    # the body= parameter of an include (which becomes markdown)
    internal = re.findall(r"\]\((/[^)\s]+)\)", body)
    internal += re.findall(r'href="(/[^"]*)"', body)
    # a path with a trailing slash is a directory, not a page
    internal = [h.rstrip("/") if not h.endswith("/blog") else h for h in internal]
    good = sum(1 for h in internal if exists(h))
    # A noindex test page is not an article and is not held to the article rules.
    is_test_page = (str(fm.get("noindex", "false")).lower() == "true"
                    or str(fm.get("sitemap", "true")).lower() == "false")
    if good < 3 and not is_test_page:
        fail("%s: only %d internal links resolve (need >= 3)" % (name, good))

    if body.lstrip().startswith("# "):
        fail("%s: body starts with an H1; the layout already renders it" % name)

    posts.setdefault(ref, {})[lang] = (name, f, excerpt)

for ref, pair in posts.items():
    if "en" in pair and "es" not in pair:
        if not os.path.isfile("_data/blog_es.yml") or ref not in read("_data/blog_es.yml"):
            notes.append("%s: EN without ES twin and without a _data/blog_es.yml entry "
                         "(the ES index will show it with the EN badge)" % ref)
    if "es" in pair and "en" not in pair:
        fail("%s: Spanish post without an English master" % ref)

# A post that opts out of indexing (noindex / sitemap: false) must not appear in
# the sitemap, in either blog index, or in either feed. The component test page
# uses this to be reachable without competing with real articles.
for f in sorted(glob.glob("_posts/*.md")):
    fm, _ = front_matter(f)
    name = os.path.basename(f)
    opted_out = (str(fm.get("sitemap", "true")).lower() == "false"
                 or str(fm.get("noindex", "false")).lower() == "true")
    if not opted_out:
        continue
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", name[:-3])
    slug = m.group(1) if m else name[:-3]
    for url in ("/blog/%s/" % slug, "/es/blog/%s/" % slug):
        if url in sitemap:
            fail("%s is marked noindex but appears in the sitemap: %s" % (name, url))
    for feeder in ("blog/Index.html", "es/blog/index.html", "blog/feed.xml", "blog/rss.xml"):
        body = read(feeder)
        if slug in body and "where_exp" not in body:
            fail("%s: the noindex post %s is not filtered out of %s"
                 % (name, slug, feeder))
    if "sitemap != false" not in read("_layouts/post.html"):
        fail("_layouts/post.html does not filter noindex posts out of the related list")

# ------------------------------------------------------------ 6/7. packaging
for excluded in ("build_sitemap.py", "check_site.py", "check_claims.py",
                 "JOURNAL_GLOSSARY.md", "JOURNAL_CHECKLIST.md", "GOOGLE_NEWS.md",
                 "build_news_sitemap.py", "sync-web.ps1"):
    if not os.path.isfile(excluded):
        continue
    if excluded not in read("_config.yml"):
        fail("%s is not listed in _config.yml exclude (Jekyll would publish it)" % excluded)
if not os.path.isfile("assets/og-card.png"):
    fail("assets/og-card.png is missing (social preview image)")

# ------------------------------------------------------------------- report
if notes:
    print("notes:")
    for n in notes:
        print("  -", n)
if problems:
    print("\nPROBLEMS (%d):" % len(problems))
    for p in problems:
        print("  x", p)
    sys.exit(1)
print("check_site.py: OK (%d sitemap urls, %d posts)" % (len(sitemap_locs), len(posts)))
