# -*- coding: utf-8 -*-
"""Generate the glossary from the two dictionaries.

Why this exists: the glossary used to be hand-maintained in six places at once
(tooltips.json, tooltips.es.json, the two _data files and the two HTML pages).
The _data files were generated correctly, but both HTML pages ended up with the
SAME definition pasted into all 68 rows -- the one for "max" -- because the row
loop kept the last entry's text instead of the current key's. Nothing caught it,
because the only check compared counts, and 68 wrong rows still count 68.

Worse, every "Details" link was broken: the page lives at /glossary/ and the
href was a bare models.html, which resolves to /glossary/models.html.

So the dictionaries are the single source of truth and everything else is
generated and validated. Run:

    python build_glossary.py            # write the four files
    python build_glossary.py --check    # fail if they are stale (used by CI)
"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.abspath(__file__))
from site_config import SITE

# Category order is editorial, not alphabetical: the page is read top to bottom
# from "what the AI is" to "what it costs".
CATS = [
    ("ai", "What the AI is", "Qué es la IA"),
    ("model", "Models and files", "Modelos y archivos"),
    ("hardware", "Hardware", "Hardware"),
    ("software", "Software and formats", "Software y formatos"),
    ("security", "Security and permissions", "Seguridad y permisos"),
    ("network", "Network and services", "Red y servicios"),
    ("product", "The product and its plans", "El producto y sus planes"),
]
VALID_CATS = {c[0].upper() for c in CATS}
BLOG_ROUTE = re.compile(r"^/?(?:es/)?blog/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?$")


def load(name):
    with io.open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return {k: v for k, v in json.load(f).items() if not k.startswith("_")}


def repo_path(route):
    """Route -> repo file. The leading slash has to go: on Windows os.path.join
    treats '\\models.html' as drive-relative and drops ROOT. The fragment goes
    too, or the '#network' ends up in the filename."""
    return os.path.join(ROOT, route.split("#")[0].lstrip("/").replace("/", os.sep))


_POSTS = None


def posts():
    """Every post with the route it really publishes at.

    Guessing from the filename is not enough: the Spanish posts declare an
    explicit permalink whose slug is the Spanish title, so
    /es/blog/2026/09/25/what-is-ai-and-how-it-works/ does not exist even though
    _posts/2026-09-25-what-is-ai-and-how-it-works.md does. The EN posts are the
    ones that fall back to the _config.yml permalink style.
    """
    global _POSTS
    if _POSTS is not None:
        return _POSTS
    rows = []
    folder = os.path.join(ROOT, "_posts")
    for name in sorted(os.listdir(folder)):
        if not name.endswith((".md", ".markdown")):
            continue
        stem = name.rsplit(".", 1)[0]
        head = io.open(os.path.join(folder, name), encoding="utf-8").read(2000)
        perm = re.search(r'^permalink:\s*"?([^"\n]+?)"?\s*$', head, re.M)
        if perm:
            route = perm.group(1).strip()
        else:
            route = "/blog/%s/%s/%s/%s/" % (stem[0:4], stem[5:7], stem[8:10], stem[11:])
        ref = re.search(r'^ref:\s*"?([^"\n]+?)"?\s*$', head, re.M)
        lang = re.search(r'^lang:\s*"?([^"\n]+?)"?\s*$', head, re.M)
        rows.append({"file": name, "route": route if route.startswith("/") else "/" + route,
                     "ref": ref.group(1).strip() if ref else None,
                     "lang": lang.group(1).strip() if lang else "en"})
    _POSTS = rows
    return rows


def post_routes():
    return {p["route"] for p in posts()}


def es_twin(route):
    """The Spanish counterpart of an English article, by shared ref."""
    src = next((p for p in posts() if p["route"] == route), None)
    if not src or not src["ref"]:
        return None
    for p in posts():
        if p["ref"] == src["ref"] and p["lang"] == "es":
            return p["route"]
    return None


def route_exists(route, lang):
    """Does this site route correspond to something that really exists?

    Blog routes are checked against the routes the posts actually publish.
    Everything else is a page in the repo root, or under es/ for the Spanish site.
    """
    bare = route.split("#")[0]
    if BLOG_ROUTE.match(bare):
        return bare in post_routes()
    if bare.lstrip("/").startswith("es/") != (lang == "es"):
        return False
    return os.path.isfile(repo_path(route))


def source_of(route):
    """The repo file a route is generated from, for anchor checks."""
    m = BLOG_ROUTE.match(route.split("#")[0])
    if m:
        y, mo, d, slug = m.groups()
        return os.path.join(ROOT, "_posts", "%s-%s-%s.md" % (y, mo, d, slug))
    return repo_path(route)


def resolve(link, lang):
    """Absolute site route for a dictionary link, preferring the ES page.

    For an article, the Spanish page points at the Spanish twin (same ref), not
    at a translated link that does not exist.
    """
    path, _, frag = link.partition("#")
    if path.startswith("http://") or path.startswith("https://"):
        return None
    if BLOG_ROUTE.match(path):
        route = "/" + path.rstrip("/") + "/"
        if lang == "es":
            twin = es_twin(route)
            if twin:
                route = twin
        return route + (("#" + frag) if frag else "")
    route = "/" + path
    if lang == "es" and route_exists("es" + route, "es"):
        route = "/es" + route
    return route + (("#" + frag) if frag else "")


def validate(en, es):
    problems = []
    if set(en) != set(es):
        for k in sorted(set(en) - set(es)):
            problems.append("'%s' is in tooltips.json but not tooltips.es.json" % k)
        for k in sorted(set(es) - set(en)):
            problems.append("'%s' is in tooltips.es.json but not tooltips.json" % k)
    for key in sorted(set(en) & set(es)):
        for label, d, lang in (("en", en[key], "en"), ("es", es[key], "es")):
            for field in ("label", "cat", "short", "link"):
                if not d.get(field):
                    problems.append("%s/%s: empty '%s'" % (label, key, field))
            if d.get("cat") and d["cat"] not in VALID_CATS:
                problems.append("%s/%s: unknown category '%s'" % (label, key, d["cat"]))
        if en[key]["cat"] != es[key]["cat"]:
            problems.append("'%s': en cat '%s' but es cat '%s'"
                            % (key, en[key]["cat"], es[key]["cat"]))
        # Every link must point at something that exists, in both languages.
        for lang in ("en", "es"):
            link = (en if lang == "en" else es)[key]["link"]
            if link.startswith("http"):
                continue
            route = resolve(link, lang)
            if route is None:
                problems.append("%s/%s: cannot resolve link '%s'" % (lang, key, link))
                continue
            if not route_exists(route, lang):
                problems.append("%s/%s: link '%s' resolves to %s, which does not exist"
                                % (lang, key, link, route))
                continue
            frag = route.partition("#")[2]
            if frag:
                body = io.open(source_of(route), encoding="utf-8").read()
                if ('id="%s"' % frag) not in body:
                    problems.append("%s/%s: link '%s' -> %s has no id=\"%s\""
                                    % (lang, key, link, route, frag))
    return problems


def ordered(d):
    """Categories in editorial order, terms alphabetical inside each.

    The dictionaries write the category upper-case ("AI"); the page anchors are
    lower-case ("cat-ai"). Normalise once, here.
    """
    out = []
    for cat, _en, _es in CATS:
        for key in sorted(k for k in d if d[k]["cat"].lower() == cat):
            out.append((key, d[key]))
    return out


def href(link, lang):
    route = resolve(link, lang)
    if route is None:
        return link
    # Liquid, not a bare href: the page lives under a subpath, so a bare
    # models.html would resolve to /glossary/models.html.
    return "{{ '%s' | relative_url }}" % route


def page(lang, en, es):
    d = en if lang == "en" else es
    other = es if lang == "en" else en
    is_en = lang == "en"
    n = len(d)

    if is_en:
        fm = ["layout: default", "title: \"Glossary\"", "permalink: /glossary/", "lang: en",
              "es_url: /es/glossary/",
              "excerpt: \"Plain definitions of the terms this site uses: model, token, context window, quantization, sandbox, permission and the rest. The same text appears as a tooltip on the pages that use it.\""]
        head = ["Glossary", "The words we use, defined.",
                "%d terms. Every definition below is the same text that appears as a tooltip on "
                "the pages that use the term. No marketing words." % n]
        cta = ('<p class="blog-meta">Missing one? <a href="https://github.com/OASISLocal/'
               'O.A.S.I.S./issues" target="_blank" rel="noopener noreferrer">Say so in Issues</a>.</p>')
        details = "Details"
    else:
        fm = ["layout: default", "title: \"Glosario\"", "permalink: /es/glossary/", "lang: es",
              "en_url: /glossary/", "es_url: /es/glossary/",
              "excerpt: \"Definiciones claras de los términos que usa este sitio: modelo, token, ventana de contexto, cuantización, sandbox, permiso y el resto. El mismo texto que aparece como tooltip en las páginas.\""]
        head = ["Glosario", "Las palabras que usamos, definidas.",
                "%d términos. Cada definición es el mismo texto que aparece como tooltip en las "
                "páginas que usan el término. Nada de palabras de marketing." % n]
        cta = ('<p class="blog-meta">¿Falta alguno? <a href="https://github.com/OASISLocal/'
               'O.A.S.I.S./issues" target="_blank" rel="noopener noreferrer">Dilo en Issues</a>.</p>')
        details = "Detalles"

    out = ["---"]
    out += fm
    out += ["---",
            '<p class="blog-eyebrow">%s</p>' % head[0],
            '<h1 class="blog-h1">%s</h1>' % head[1],
            '<p class="blog-meta">%s</p>' % head[2],
            ""]

    for cat, cat_en, cat_es in CATS:
        rows = [(k, v) for k, v in ordered(d) if v["cat"].lower() == cat]
        if not rows:
            continue
        out.append('  <h2 id="cat-%s">%s</h2>' % (cat, cat_en if is_en else cat_es))
        out.append('  <table class="glossary">')
        out.append('    <thead><tr><th scope="col">%s</th><th scope="col">%s</th></tr></thead>'
                   % ("Term" if is_en else "Término",
                      "What it means here" if is_en else "Qué significa aquí"))
        out.append("    <tbody>")
        for key, t in rows:
            out.append('      <tr id="g-%s">' % key)
            # The EN page carries the Spanish rendering, but only when it is
            # actually different: "ES: Token" next to "Token" is noise.
            if is_en:
                es_label = other[key]["label"]
                if es_label.strip().lower() != t["label"].strip().lower():
                    out.append('        <th scope="row"><span class="term" data-term="%s">%s</span>'
                               ' <span class="gl-es">ES: %s</span></th>' % (key, t["label"], es_label))
                else:
                    out.append('        <th scope="row"><span class="term" data-term="%s">%s</span></th>'
                               % (key, t["label"]))
            else:
                out.append('        <th scope="row"><span class="term" data-term="%s">%s</span></th>'
                           % (key, t["label"]))
            out.append('        <td>%s <a href="%s">%s</a></td>'
                       % (t["short"], href(t["link"], lang), details))
            out.append("      </tr>")
        out.append("    </tbody>")
        out.append("  </table>")
        out.append("")

    out.append(cta)
    out.append("")
    return "\n".join(out)


def jsonld(lang, d):
    is_en = lang == "en"
    base = SITE + ("/glossary/" if is_en else "/es/glossary/")
    home = SITE + ("/" if is_en else "/es/")
    page_id = base + "#glossary"
    name = "Glossary" if is_en else "Glosario"
    set_name = "O.A.S.I.S. glossary" if is_en else "Glosario de O.A.S.I.S."
    desc = ("Plain definitions of the terms used across the O.A.S.I.S. product, website and Journal."
            if is_en else
            "Definiciones claras de los términos usados en el producto, el sitio y el Journal de O.A.S.I.S.")

    terms = []
    for key, t in ordered(d):
        route = resolve(t["link"], lang)
        # The anchor is dropped: a schema.org url must be a document, and every
        # term here resolves to a section of the page named in link.
        url = t["link"] if route is None else SITE + route.partition("#")[0]
        terms.append({
            "@type": "DefinedTerm",
            "@id": base + "#g-" + key,
            "name": t["label"],
            "description": t["short"],
            "inDefinedTermSet": {"@id": page_id},
            "url": url,
        })

    graph = [
        {"@type": "DefinedTermSet", "@id": page_id, "name": set_name,
         "description": desc, "url": base, "inLanguage": lang, "hasDefinedTerm": terms},
        {"@type": "WebPage", "@id": base + "#webpage", "url": base, "name": name,
         "description": "Plain definitions of the terms this site uses." if is_en
                        else "Definiciones claras de los términos que usa este sitio.",
         "inLanguage": lang, "isPartOf": {"@id": SITE + "/#website"},
         "breadcrumb": {"@id": base + "#breadcrumb"}},
        {"@type": "BreadcrumbList", "@id": base + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home" if is_en else "Inicio",
             "item": home},
            {"@type": "ListItem", "position": 2, "name": name, "item": base},
        ]},
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      indent=2, ensure_ascii=False) + "\n"


def validate_posts(en, es):
    """Every data-term used in a post must exist in the dictionary.

    tooltip.js looks the key up and does nothing when it is missing, so a typo
    like data-term="tokeniser" would ship a word with no tooltip and no error.
    """
    problems = []
    folder = os.path.join(ROOT, "_posts")
    for name in sorted(os.listdir(folder)):
        if not name.endswith((".md", ".markdown")):
            continue
        text = io.open(os.path.join(folder, name), encoding="utf-8").read()
        head = text[:1200]
        lang = "es" if re.search(r'^lang:\s*"?es"?\s*$', head, re.M) else "en"
        d = es if lang == "es" else en
        for key in sorted(set(re.findall(r'data-term="([^"]+)"', text))):
            if key not in d:
                problems.append("_posts/%s (lang=%s) uses data-term=\"%s\", "
                                "which is not in tooltips%s.json"
                                % (name, lang, key, ".es" if lang == "es" else ""))
    return problems


def build():
    en, es = load("tooltips.json"), load("tooltips.es.json")
    problems = validate(en, es) + validate_posts(en, es)
    files = None
    if not problems:
        files = {
            "glossary.html": page("en", en, es),
            "es/glossary.html": page("es", en, es),
            "_data/glossary_terms.json": jsonld("en", en),
            "_data/glossary_terms_es.json": jsonld("es", es),
        }
        # Without layout: default the page renders with no <head> at all: no
        # charset, no CSS, no navigation. Every DOM check still passed, because
        # the rows were there -- only a screenshot showed the missing site.
        for name in ("glossary.html", "es/glossary.html"):
            if not files[name].startswith("---\nlayout: default\n"):
                problems.append("%s: front matter must start with 'layout: default'" % name)
    if problems:
        print("build_glossary: %d problem(s):" % len(problems))
        for p in problems:
            print("  x " + p)
        return None
    return files


def main():
    files = build()
    if files is None:
        return 1
    if "--check" in sys.argv:
        stale = []
        for name, want in files.items():
            path = os.path.join(ROOT, name.replace("/", os.sep))
            have = io.open(path, encoding="utf-8").read() if os.path.isfile(path) else ""
            if have != want:
                stale.append(name)
        if stale:
            print("build_glossary --check: generated files are stale: %s" % ", ".join(stale))
            print("  run: python build_glossary.py")
            return 1
        print("build_glossary --check: OK (%d files up to date)" % len(files))
        return 0
    for name, text in files.items():
        path = os.path.join(ROOT, name.replace("/", os.sep))
        parent = os.path.dirname(path)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent)
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print("wrote %s (%d bytes)" % (name, len(text.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
