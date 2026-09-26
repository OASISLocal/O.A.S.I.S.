# -*- coding: utf-8 -*-
"""Google News sitemap — PREPARED BUT NOT ACTIVATED.

Google News only indexes articles published in the last ~48 hours, so a news
sitemap is a stream, not a list. It is generated from the Journal posts and is
intentionally NOT referenced from robots.txt yet: see GOOGLE_NEWS.md for the
activation steps and why they are being done by hand.

    python build_news_sitemap.py            # writes news-sitemap.xml
    python build_news_sitemap.py --check    # exit 1 if it would change
    python build_news_sitemap.py --missing  # explain what activation needs
"""
import io, os, re, sys, glob, time, datetime
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
from site_config import SITE
PUBLICATION = "O.A.S.I.S. Journal"
WINDOW_DAYS = 2          # Google News keeps ~48h of articles in a news sitemap
ACTIVATED = False        # flip to True only when the Publisher Center is verified

NEWS_NS = "http://www.google.com/schemas/sitemap-news/0.9"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NS = "http://www.w3.org/1999/xhtml"


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


def collect():
    """Posts inside the news window, newest first, with their ES twin."""
    now = datetime.datetime.now()
    out = []
    for f in sorted(glob.glob("_posts/*.md")):
        src = read(f)
        fm = front_matter(src)
        if fm.get("lang", "en") != "en":
            continue
        name = os.path.basename(f)[:-3]
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$", name)
        if not m:
            continue
        d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if (now.date() - d).days > WINDOW_DAYS:
            continue
        perm = fm.get("permalink") or "/blog/%s/%s/%s/%s/" % m.groups()
        out.append({
            "date": d,
            "url": perm,
            "title": fm.get("title", ""),
            "excerpt": fm.get("excerpt", ""),
            "ref": fm.get("ref") or m.group(4),
        })
    out.sort(key=lambda p: p["date"], reverse=True)
    return out


def es_twin(ref):
    for f in sorted(glob.glob("_posts/*.md")):
        src = read(f)
        fm = front_matter(src)
        if fm.get("lang") == "es" and (fm.get("ref") or os.path.basename(f)[:-3][11:]) == ref:
            return fm.get("permalink")
    return None


def build():
    ET.register_namespace("", SITEMAP_NS)
    ET.register_namespace("news", NEWS_NS)
    ET.register_namespace("xhtml", XHTML_NS)
    root = ET.Element("urlset")
    for p in collect():
        u = ET.SubElement(root, "{%s}url" % SITEMAP_NS)
        ET.SubElement(u, "{%s}loc" % SITEMAP_NS).text = SITE + p["url"]
        n = ET.SubElement(u, "{%s}news" % NEWS_NS)
        pub = ET.SubElement(n, "{%s}publication" % NEWS_NS)
        ET.SubElement(pub, "{%s}name" % NEWS_NS).text = PUBLICATION
        ET.SubElement(pub, "{%s}language" % NEWS_NS).text = "en"
        art = ET.SubElement(n, "{%s}article" % NEWS_NS)
        ET.SubElement(art, "{%s}publication_date" % NEWS_NS).text = p["date"].isoformat()
        ET.SubElement(art, "{%s}title" % NEWS_NS).text = p["title"]
        es = es_twin(p["ref"])
        if es:
            ET.SubElement(art, "{%s}alternative_loc" % NEWS_NS).text = SITE + es
        # hreflang alternates, same as the main sitemap
        for hl, href in (("en", p["url"]), ("es", es or p["url"]), ("x-default", p["url"])):
            if hl == "es" and not es:
                continue
            lk = ET.SubElement(u, "{%s}link" % XHTML_NS)
            lk.set("rel", "alternate")
            lk.set("hreflang", hl)
            lk.set("href", SITE + href)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")


def main():
    out = build()
    target = "news-sitemap.xml"
    current = read(target) if os.path.isfile(target) else None
    if "--check" in sys.argv:
        if current != out + "\n":
            print("build_news_sitemap.py --check: %s is out of date" % target)
            sys.exit(1)
        print("%s up to date (%d articles in window)" % (target, out.count("<news:article>")))
        return
    if "--missing" in sys.argv:
        print("ACTIVATED = %s in build_news_sitemap.py" % ACTIVATED)
        print("articles inside the %d-day window: %d" % (WINDOW_DAYS, out.count("<news:article>")))
        print("\nTo turn Google News on (not done yet):")
        print("  1. verify the domain in Google News Publisher Center")
        print("  2. set ACTIVATED = True in build_news_sitemap.py")
        print("  3. add the news-sitemap line to robots.txt")
        print("  4. link the RSS feed: <link rel=alternate type=application/rss+xml>")
        print("  5. submit news-sitemap.xml + /blog/rss.xml in Search Console")
        return
    with io.open(target, "w", encoding="utf-8", newline="") as f:
        f.write(out + "\n")
    print("%s regenerated: %d articles in the %d-day window" % (target, out.count("<news:article>"), WINDOW_DAYS))
    if not ACTIVATED:
        print("remember: it is generated but NOT referenced from robots.txt (dormant)")


if __name__ == "__main__":
    main()
