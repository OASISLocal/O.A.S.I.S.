# -*- coding: utf-8 -*-
"""Generate the FAQPage schema on the two product FAQ pages from their own
visible questions.

Those two pages carry a hand-written FAQPage block, and it had drifted: the
schema asked "Does OASIS really work offline?" while the page says "Does it
really work offline?", and the order differed too. Nothing caught it, because
nothing compared the two.

The visible <details> list is the better text, so it is the source. This
rewrites the block between markers from what the reader actually sees, which
makes the two impossible to disagree.

    python build_faqpage.py            # write
    python build_faqpage.py --check    # fail if stale (run by sync-web.ps1)
"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.abspath(__file__))
from site_config import SITE

PAGES = ["faq.html", os.path.join("es", "faq.html")]
START = "<!-- faqpage:generated -->"
END = "<!-- /faqpage:generated -->"

# The first item is <details open>, the rest <details>: matching "<details>"
# exactly silently dropped the first question.
ITEM = re.compile(r"<details[^>]*>\s*<summary>(.*?)</summary>(.*?)</details>", re.S)
SCRIPT_FAQ = re.compile(
    r'<script type="application/ld\+json">\s*(\{"@context":\s*"https://schema\.org",\s*'
    r'"@type":\s*"FAQPage".*?)</script>', re.S)


def plain(fragment):
    """Markup to text, with the spacing a reader would see."""
    t = re.sub(r"<[^>]+>", "", fragment)
    t = (t.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
          .replace("&#39;", "'").replace("&mdash;", "-").replace("&lt;", "<")
          .replace("&gt;", ">"))
    return re.sub(r"\s+", " ", t).strip()


def extract(html):
    out = []
    for q_html, a_html in ITEM.findall(html):
        q = plain(q_html)
        a = plain(a_html)
        if q and a:
            out.append((q, a))
    return out


def block(pairs, page_url):
    entities = [{
        "@type": "Question",
        "name": q,
        "acceptedAnswer": {"@type": "Answer", "text": a},
    } for q, a in pairs]
    doc = {"@context": "https://schema.org", "@type": "FAQPage",
           "url": page_url, "mainEntity": entities}
    return ('<script type="application/ld+json">'
            + json.dumps(doc, indent=2, ensure_ascii=False)
            + "</script>")


def rebuild(html, page_url, add_markers):
    pairs = extract(html)
    if not pairs:
        return None, []
    new = block(pairs, page_url)
    if START in html and END in html:
        out = re.sub(re.escape(START) + r".*?" + re.escape(END),
                     START + "\n" + new + "\n" + END, html, flags=re.S)
    else:
        out, n = SCRIPT_FAQ.subn(lambda m: new, html, count=1)
        if n and add_markers:
            out = out.replace(new, START + "\n" + new + "\n" + END, 1)
    return out, pairs


def main():
    problems = []
    changed = []
    for page in PAGES:
        path = os.path.join(ROOT, page.replace("/", os.sep))
        html = io.open(path, encoding="utf-8").read()
        rel = page.replace(os.sep, "/")          # "es\faq.html" -> "es/faq.html"
        url = SITE + "/" + rel
        out, pairs = rebuild(html, url, add_markers="--check" not in sys.argv)
        if out is None:
            problems.append("%s: no <details><summary> FAQ items found to read" % page)
            continue
        if not pairs:
            problems.append("%s: no usable question/answer pairs" % page)
            continue
        if out != html:
            changed.append("%s (%d questions)" % (page, len(pairs)))
            if "--check" not in sys.argv:
                with io.open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(out)
        if "--check" in sys.argv and out != html:
            problems.append("%s: the FAQPage block does not match the visible FAQ "
                            "(%d questions). Run: python build_faqpage.py" % (page, len(pairs)))

    if problems:
        print("build_faqpage: %d problem(s):" % len(problems))
        for p in problems:
            print("  x " + p)
        return 1
    if "--check" in sys.argv:
        print("build_faqpage --check: OK (el schema coincide con el FAQ visible)")
        return 0
    for c in changed:
        print("  rewrote FAQPage in %s" % c)
    if not changed:
        print("  nothing to rewrite")
    return 0


if __name__ == "__main__":
    sys.exit(main())
