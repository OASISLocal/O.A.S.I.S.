# -*- coding: utf-8 -*-
"""Regenerate sitemap.xml from the repository itself.

Why this exists: with 40 Journal articles there are ~80 new URLs, each of which
used to be a manual edit. The sitemap is now derived from the files:

  * static pages: the PAGES table below (path, lastmod, changefreq, priority)
  * Journal posts: read from _posts/*.md front matter (date, lang, ref, permalink)

Emitted format is byte-identical to the hand-maintained sitemap it replaces.
Run:  python build_sitemap.py            (writes sitemap.xml)
      python build_sitemap.py --check    (fails if it would change anything)
"""
import io, os, re, sys, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
SITE = "https://oasislocal.github.io/O.A.S.I.S."

# path, lastmod, changefreq, priority — order is the published order.
PAGES = [
    ("/", "2026-09-21", "weekly", "1.0"),
    ("/how-it-works.html", "2026-09-21", "monthly", "0.9"),
    ("/requirements.html", "2026-09-21", "monthly", "0.9"),
    ("/download.html", "2026-09-21", "monthly", "0.9"),
    ("/pricing.html", "2026-09-21", "monthly", "0.8"),
    ("/models.html", "2026-09-21", "monthly", "0.8"),
    ("/tools.html", "2026-09-21", "monthly", "0.8"),
    ("/comparison.html", "2026-09-21", "monthly", "0.8"),
    ("/features.html", "2026-09-21", "monthly", "0.8"),
    ("/faq.html", "2026-09-21", "monthly", "0.8"),
    ("/security.html", "2026-09-21", "yearly", "0.6"),
    ("/changelog.html", "2026-09-21", "monthly", "0.6"),
    ("/about.html", "2026-09-21", "yearly", "0.6"),
    ("/privacy.html", "2026-09-21", "yearly", "0.5"),
    ("/privacy-policy.html", "2026-09-21", "yearly", "0.6"),
    ("/eula.html", "2026-09-21", "yearly", "0.5"),
    ("/third-party-notices.html", "2026-09-21", "yearly", "0.5"),
    ("/blog/", "2026-09-25", "weekly", "0.7"),
]

# /es/blog/ has its own entry (x-default points at the English index).
EXTRA = [("/es/blog/", "/blog/", "2026-09-25", "weekly", "0.7")]

# Explicit ES twins for paths that are not "<page>.html" under /es/.
ES_TWINS = {
    "/": "/es/",
    "/blog/": "/es/blog/",
}


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def front_matter(path):
    """Return the parsed YAML front matter of a Jekyll file (simple subset)."""
    src = read(path)
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", src, re.S)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split("\n"):
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        if v.startswith(("'", '"')) and v.endswith(("'", '"')) and len(v) > 1:
            v = v[1:-1]
        fm[k.strip()] = v
    return fm


def es_url_for(path):
    """The Spanish twin of a static page path, or None."""
    if path in ES_TWINS:
        return ES_TWINS[path]
    if not path.endswith(".html"):
        return None
    candidate = "/es" + path
    return candidate if os.path.isfile("." + candidate) else None


def load_posts():
    """Journal posts grouped by ref: {ref: {"en": (url, date), "es": (url, date)}}."""
    posts = {}
    for f in sorted(glob.glob("_posts/*.md")):
        fm = front_matter(f)
        lang = fm.get("lang", "en")
        slug = os.path.basename(f)[:-3]          # 2026-09-25-what-is-ai
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$", slug)
        if not m:
            print("WARN: cannot parse date from %s" % f)
            continue
        date = "%s-%s-%s" % m.groups()[:3]
        if "permalink" in fm:
            url = fm["permalink"]
        else:
            url = "/blog/%s/%s/%s/%s/" % (m.group(1), m.group(2), m.group(3), m.group(4))
        ref = fm.get("ref") or m.group(4)
        posts.setdefault(ref, {})[lang] = (url, date)
    return posts


def url_entry(loc, en, es, lastmod, changefreq, priority):
    def alt(hreflang, href):
        return '<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (hreflang, href)
    parts = ['<url><loc>%s%s</loc>' % (SITE, loc)]
    parts.append(alt("en", SITE + en))
    parts.append(alt("es", SITE + es))
    parts.append(alt("x-default", SITE + en))
    parts.append("<lastmod>%s</lastmod>" % lastmod)
    parts.append("<changefreq>%s</changefreq>" % changefreq)
    parts.append("<priority>%s</priority>" % priority)
    parts.append("</url>")
    return "".join(parts)


def build():
    entries = []
    for path, lastmod, freq, prio in PAGES:
        es = es_url_for(path) or path
        entries.append(url_entry(path, path, es, lastmod, freq, prio))
    for loc, x_default, lastmod, freq, prio in EXTRA:
        entries.append(url_entry(loc, x_default, loc, lastmod, freq, prio))

    posts = load_posts()
    def key(item):
        return item[1]["en"][1] if "en" in item[1] else item[1]["es"][1]
    for ref, pair in sorted(posts.items(), key=key, reverse=True):
        lastmod = (pair.get("en") or pair.get("es"))[1]
        if "en" in pair:
            en_url, _ = pair["en"]
            es_url = pair["es"][0] if "es" in pair else en_url
            entries.append(url_entry(en_url, en_url, es_url, lastmod, "yearly", "0.7"))
            if "es" in pair:
                es_url = pair["es"][0]
                entries.append(url_entry(es_url, en_url, es_url, lastmod, "yearly", "0.6"))
        else:
            es_url, _ = pair["es"]
            entries.append(url_entry(es_url, es_url, es_url, lastmod, "yearly", "0.6"))

    header = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
              'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n  ')
    return header + "\n  ".join(entries) + "</urlset>\n"


def main():
    out = build()
    target = os.path.join(ROOT, "sitemap.xml")
    current = read("sitemap.xml") if os.path.isfile(target) else ""
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
    with io.open(target, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    print("sitemap.xml regenerated: %d urls (%d before)" % (out.count("<url>"), current.count("<url>")))


if __name__ == "__main__":
    main()
