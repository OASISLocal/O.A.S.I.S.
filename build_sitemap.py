# -*- coding: utf-8 -*-
"""Regenerate sitemap.xml from the repository itself.

Why this exists: with 40 Journal articles there are ~80 new URLs, each of which
used to be a manual edit. The sitemap is now derived from the files:

  * static pages: the PAGES table below, lastmod taken from the last commit
    that touched each file (`git log -1 --format=%as -- <path>`)
  * Journal posts: read from _posts/*.md front matter (date, lang, ref, permalink)

Two rules from docs/PLAN_BUSCADORES_2026.md (Fase 0):

  1. Every Spanish twin is emitted as its OWN <url>, with hreflang pointing
     back to its English page. A mirror reachable only through an alternate is
     discovered late; a mirror declared as a URL is discovered on schedule.
  2. `lastmod` is real (the commit date), never a hand-typed constant.

`changefreq` and `priority` are deliberately NOT emitted. Google ignores both
completely, and hand-maintained values are false precision that rots: for the
site that exists, the truth is "this page changed in this commit".

Run:  python build_sitemap.py            (writes sitemap.xml)
      python build_sitemap.py --check    (exit 1 if it would change anything)
"""
import io, os, re, sys, glob, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
SITE = "https://oasislocal.github.io/O.A.S.I.S."
FALLBACK_LASTMOD = "2026-09-21"          # only if git has no history for a file

# Site path -> the file that produces it. Order is the published order.
PAGES = [
    ("/", "index.html"),
    ("/how-it-works.html", "how-it-works.html"),
    ("/requirements.html", "requirements.html"),
    ("/download.html", "download.html"),
    ("/pricing.html", "pricing.html"),
    ("/models.html", "models.html"),
    ("/tools.html", "tools.html"),
    ("/comparison.html", "comparison.html"),
    ("/features.html", "features.html"),
    ("/faq.html", "faq.html"),
    ("/security.html", "security.html"),
    ("/changelog.html", "changelog.html"),
    ("/about.html", "about.html"),
    ("/privacy.html", "privacy.html"),
    ("/privacy-policy.html", "privacy-policy.html"),
    ("/eula.html", "eula.html"),
    ("/third-party-notices.html", "third-party-notices.html"),
    ("/blog/", "blog/Index.html"),
    ("/glossary/", "glossary.html"),
]

# Paths whose Spanish twin is not "<page>.html" under /es/.
ES_TWINS = {"/": "/es/", "/blog/": "/es/blog/", "/glossary/": "/es/glossary/"}

_git_cache = {}


def git_lastmod(path):
    """Date of the last commit that touched `path` (YYYY-MM-DD), or the fallback."""
    if path in _git_cache:
        return _git_cache[path]
    out = FALLBACK_LASTMOD
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%as", "--", path],
                           capture_output=True, text=True, timeout=20)
        value = (r.stdout or "").strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            out = value
    except Exception:
        pass
    _git_cache[path] = out
    return out


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def front_matter(path):
    src = read(path)
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


def es_url_for(path):
    """The Spanish twin of a site path, or None when there is none."""
    if path in ES_TWINS:
        return ES_TWINS[path]
    if not path.endswith(".html"):
        return None
    candidate = "/es" + path
    return candidate if os.path.isfile("." + candidate) else None


def es_source_for(site_path):
    """The local file that produces a Spanish site path."""
    if not site_path:
        return None
    rel = site_path.strip("/")
    if not rel:
        rel = "index.html"
    elif site_path.endswith("/"):
        rel = rel + "/index.html"
    for cand in (rel, rel.replace("index.html", "Index.html")):
        if os.path.isfile(cand):
            return cand
    return None


def load_posts():
    """Posts grouped by ref: {ref: {"en": (url, date, file), "es": (...)}}."""
    posts = {}
    for f in sorted(glob.glob("_posts/*.md")):
        fm = front_matter(f)
        lang = fm.get("lang", "en")
        slug = os.path.basename(f)[:-3]
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$", slug)
        if not m:
            print("WARN: cannot parse date from %s" % f)
            continue
        # A post can opt out of the sitemap (used by the component test page).
        if str(fm.get("sitemap", "true")).lower() == "false":
            continue
        date = "%s-%s-%s" % m.groups()[:3]
        url = fm.get("permalink") or "/blog/%s/%s/%s/%s/" % m.groups()
        ref = fm.get("ref") or m.group(4)
        posts.setdefault(ref, {})[lang] = (url, date, f)
    return posts


def url_entry(loc, en, es, lastmod):
    """One <url> with the three hreflang alternates it participates in."""
    def alt(hreflang, href):
        return '<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (hreflang, href)
    return ("".join([
        "<url><loc>%s%s</loc>" % (SITE, loc),
        alt("en", SITE + en),
        alt("es", SITE + es),
        alt("x-default", SITE + en),
        "<lastmod>%s</lastmod>" % lastmod,
        "</url>",
    ]))


def build():
    entries = []
    for path, source in PAGES:
        es = es_url_for(path)
        lastmod = git_lastmod(source)
        # English page: hreflang self + Spanish twin + x-default to English
        entries.append(url_entry(path, path, es or path, lastmod))
        # Spanish twin: its own <url>, hreflang pointing back at the English page
        if es:
            es_source = es_source_for(es)
            es_lastmod = git_lastmod(es_source) if es_source else lastmod
            entries.append(url_entry(es, path, es, es_lastmod))

    posts = load_posts()
    def key(item):
        pair = item[1]
        return (pair.get("en") or pair.get("es"))[1]

    for ref, pair in sorted(posts.items(), key=key, reverse=True):
        if "en" in pair:
            en_url, en_date, _ = pair["en"]
            if "es" in pair:
                es_url, es_date, _ = pair["es"]
                entries.append(url_entry(en_url, en_url, es_url, en_date))
                entries.append(url_entry(es_url, en_url, es_url, es_date))
            else:
                # English only: no misleading hreflang es
                entries.append("<url><loc>%s%s</loc><xhtml:link rel=\"alternate\" "
                               "hreflang=\"en\" href=\"%s%s\"/><xhtml:link rel=\"alternate\" "
                               "hreflang=\"x-default\" href=\"%s%s\"/><lastmod>%s</lastmod></url>"
                               % (SITE, en_url, SITE, en_url, SITE, en_url, en_date))
        else:
            es_url, es_date, _ = pair["es"]
            entries.append(url_entry(es_url, es_url, es_url, es_date))

    header = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
              'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n  ')
    return header + "\n  ".join(entries) + "</urlset>\n"


def main():
    out = build()
    current = read("sitemap.xml") if os.path.isfile("sitemap.xml") else ""
    if "--check" in sys.argv:
        if current != out:
            print("build_sitemap.py --check: sitemap.xml is out of date")
            print("run: python build_sitemap.py")
            sys.exit(1)
        print("sitemap.xml is up to date (%d urls)" % out.count("<url>"))
        return
    if current == out:
        print("sitemap.xml already up to date (%d urls)" % out.count("<url>"))
        return
    with io.open("sitemap.xml", "w", encoding="utf-8", newline="") as f:
        f.write(out)
    print("sitemap.xml regenerated: %d urls (%d before)" % (out.count("<url>"), current.count("<url>")))


if __name__ == "__main__":
    main()
