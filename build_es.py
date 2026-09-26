# -*- coding: utf-8 -*-
"""Build es/ pages from the English originals.
   Translations live in i18n/_shared.json (applied everywhere) and i18n/<page>.json
   (each a list of [english_substring, spanish_substring]). Every English string
   must be found, otherwise the build fails loudly.

   --check regenerates every page in memory and compares it with the committed
   es/ file, writing nothing. It exists because a plain run silently overwrites
   all of es/, and Spanish text edited by hand in there (a paragraph added
   outside i18n/, a hreflang tag, a fixed title) disappeared without anyone
   noticing until the page was read again. The gate turns that into a failure
   you have to look at."""
import io, os, re, json, sys, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
I18N = os.path.join(ROOT, 'i18n')
from site_config import BASEURL, SITE
# BASE is the absolute origin the ES pages declare in canonical/og:url, so it
# needs the host as well as the subpath. PATH is the subpath on its own, for the
# hrefs written into these static pages.
BASE = SITE + '/'
# Path-only form of BASE. The es/ pages are static HTML with no front matter, so
# they cannot use relative_url; they carry absolute paths like the rest of the
# site instead of "../" climbing out of /es/.
PATH = BASEURL
PAGES = ['index.html', '404.html', 'about.html', 'changelog.html', 'comparison.html',
         'download.html', 'eula.html', 'faq.html', 'features.html', 'how-it-works.html',
         'models.html', 'pricing.html', 'privacy.html', 'privacy-policy.html',
         'requirements.html', 'security.html', 'third-party-notices.html', 'tools.html']

def load(name):
    p = os.path.join(I18N, name)
    if not os.path.exists(p):
        return []
    return json.load(io.open(p, encoding='utf-8'))

MISSES = []

def apply_pairs(html, pairs, where, strict=True):
    for pair in sorted(pairs, key=lambda p: len(p[0]), reverse=True):
        en, es = pair[0], pair[1]
        if en not in html:
            if strict:
                MISSES.append('[%s] %r' % (where, en[:110]))
            continue
        html = html.replace(en, es)
    return html

def en_url(page):
    return BASE if page == 'index.html' else BASE + page

def es_url(page):
    return BASE + 'es/' if page == 'index.html' else BASE + 'es/' + page

def to_spanish(html, page):
    # html lang
    html = re.sub(r'(<html[^>]*\blang=")en(")', r'\1es\2', html, count=1)
    # canonical + og:url  (EN -> ES)
    html = html.replace('<link rel="canonical" href="%s">' % en_url(page),
                        '<link rel="canonical" href="%s">' % es_url(page))
    html = html.replace('<meta property="og:url" content="%s">' % en_url(page),
                        '<meta property="og:url" content="%s">' % es_url(page))
    html = html.replace('<meta property="og:locale" content="en_US">',
                        '<meta property="og:locale" content="es_ES">')
    # og:locale:alternate is the *other* language, so on the Spanish page it has
    # to point back at English. It was left at en_US->es_ES by the replace above
    # (different string, so it survived untouched) and then corrected by hand in
    # all 15 es/ files, which is exactly the kind of edit a regeneration erases.
    html = html.replace('<meta property="og:locale:alternate" content="es_ES">',
                        '<meta property="og:locale:alternate" content="en_US">')
    # Paths. Absolute, not "../": the es/ pages live one level down, so a
    # relative link works right up until the depth changes, and "../blog/" sent
    # the Spanish reader to the English Journal. check_lang.py can only police
    # links it can see, and it could not see a relative one.
    html = html.replace('href="assets/', 'href="%sassets/' % PATH)
    html = html.replace('src="assets/', 'src="%sassets/' % PATH)
    html = html.replace('href="favicon.ico"', 'href="%sfavicon.ico"' % PATH)
    # The Journal in Spanish, not the English one.
    html = html.replace('href="blog/', 'href="%ses/blog/' % PATH)
    html = html.replace('href="es/blog/', 'href="%ses/blog/' % PATH)
    # llms.txt has no Spanish twin, but a relative "llms.txt" from /es/ resolves
    # to /es/llms.txt, which does not exist. Absolute, and check_site catches it
    # if this ever comes back.
    html = html.replace('href="llms.txt"', 'href="%sllms.txt"' % PATH)
    # Any es/ link left over in the body: same problem, one directory deeper.
    html = re.sub(r'href="es/([^"]*)"', lambda m: 'href="%ses/%s"' % (PATH, m.group(1)), html)
    # language switcher: ES link -> absolute EN link back to the original
    en_path = PATH if page == 'index.html' else PATH + page
    html = re.sub(r'<a href="es/[^"]*"[^>]*>ES</a>',
                  '<a class="lang-switch" href="%s" lang="en" hreflang="en" data-lang-switch="en">EN</a>' % en_path,
                  html)
    html = re.sub(r'<a class="btn ghost" href="es/"[^>]*>Espa�ol</a>',
                  '<a class="btn ghost" href="%s" hreflang="en" lang="en" data-lang-switch="en">English</a>' % en_path, html)
    # language assets
    if 'lang.css' not in html:
        html = html.replace('</head>', '<link rel="stylesheet" href="%sassets/lang.css">\n</head>' % PATH, 1)
    if 'lang.js' not in html:
        html = html.replace('</body>', '<script src="%sassets/lang.js"></script>\n</body>' % PATH, 1)
    return html

def to_spanish_legal(html, page):
    """Jekyll front-matter pages (legal): swap lang, move permalink under /es/,
       and point same-site Liquid links at the Spanish copies."""
    html = re.sub(r'^lang: en\r?$', 'lang: es', html, count=1, flags=re.M)
    html = re.sub(r'^permalink: /([^\r\n]+)$', lambda m: 'permalink: /es/' + m.group(1), html, count=1, flags=re.M)
    html = re.sub(r"\{\{ '(/[^']+\.html)' \| relative_url \}\}",
                  lambda m: "{{ '/es%s' | relative_url }}" % m.group(1), html)
    html = html.replace('href="assets/fonts/LICENSE.txt"',
                        'href="{{ \'/assets/fonts/LICENSE.txt\' | relative_url }}"')
    return html

def patch_english(html):
    # switcher remembers the choice
    html = re.sub(r'(<a href="es/[^"]*"[^>]*?)>ES</a>',
                  lambda m: (m.group(1) + ' data-lang-switch="es">ES</a>')
                  if 'data-lang-switch' not in m.group(1) else m.group(0), html)
    html = html.replace('<a class="btn ghost" href="es/">Español</a>',
                        '<a class="btn ghost" href="es/" data-lang-switch="es">Español</a>')
    if 'lang.css' not in html:
        html = html.replace('</head>', '<link rel="stylesheet" href="assets/lang.css">\n</head>', 1)
    if 'lang.js' not in html:
        html = html.replace('</body>', '<script src="assets/lang.js"></script>\n</body>', 1)
    return html

def summarise(current, generated):
    """One line per page that says what regeneration would change, in terms an
    editor can act on. A bare 'differs' made this gate something people learn to
    ignore, which is the same as no gate at all."""
    old = set(current.splitlines())
    new = set(generated.splitlines())
    gone = [l for l in old - new if l.strip()]
    fresh = [l for l in new - old if l.strip()]
    bits = []
    if gone:
        bits.append('%d linea(s) hand-written que se perderian' % len(gone))
    if fresh:
        bits.append('%d linea(s) nuevas' % len(fresh))
    out = ', '.join(bits) if bits else 'difiere en el orden de las lineas'
    if gone:
        out += ' | ejemplo que se pierde: ' + gone[0].strip()[:100]
    return out

def render_es(page, shared, attrs):
    """The Spanish page as it *would* be written. Pure: reads, never writes."""
    src = os.path.join(ROOT, page)
    if not os.path.exists(src):
        return None
    html = io.open(src, encoding='utf-8', newline='').read()
    html = apply_pairs(html, load(page + '.json'), page)
    html = apply_pairs(html, attrs, page, strict=False)
    html = apply_pairs(html, shared, page, strict=False)
    if html.lstrip().startswith('---'):
        return to_spanish_legal(html, page)
    return to_spanish(html, page)

def main():
    check = '--check' in sys.argv[1:]
    shared = load('_shared.json')
    attrs = load('_attrs.json')

    # 1) patch the English pages (switcher attr + language assets)
    en_dirty = []
    for page in PAGES:
        src = os.path.join(ROOT, page)
        if not os.path.exists(src):
            continue
        html = io.open(src, encoding='utf-8', newline='').read()
        out = patch_english(html)
        if out != html:
            en_dirty.append(page)
            if not check:
                io.open(src, 'w', encoding='utf-8', newline='').write(out)
                print('EN patched  ', page)

    # 2) build the Spanish pages, or just compare them
    stale = []
    if not check:
        os.makedirs(os.path.join(ROOT, 'es'), exist_ok=True)
    for page in PAGES:
        html = render_es(page, shared, attrs)
        if html is None:
            print('skip (missing)', page); continue
        dst = os.path.join(ROOT, 'es', page)
        if check:
            if not os.path.exists(dst):
                stale.append((page, 'no hay fichero commiteado'))
                continue
            current = io.open(dst, encoding='utf-8', newline='').read()
            if current != html:
                stale.append((page, summarise(current, html)))
        else:
            io.open(dst, 'w', encoding='utf-8', newline='').write(html)
            print('ES built     ', page)

    if check:
        # A stale page is not automatically a bug: it can be the signal that
        # i18n/ was updated and es/ has not been regenerated yet. Either way the
        # answer is the same, look at it before committing.
        if stale or en_dirty:
            print('--- STALE (%d) ---' % len(stale))
            for page, why in stale:
                print('[%s] %s' % (page, why))
            if en_dirty:
                print('Los originales EN cambiarian al ejecutar el script: %s'
                      % ', '.join(en_dirty))
            print('build_es.py --check: lo commiteado en es/ no coincide con lo que')
            print('genera este script. Revisa el diff antes de seguir.')
            print('Si el cambio es intencionado, ejecuta: python build_es.py')
            sys.exit(1)
        print('build_es.py --check: es/ esta sincronizado con i18n/ (%d paginas).'
              % len(PAGES))
        return

    print('done')
    if MISSES:
        # Report first, then fail. The exit used to come first, so the list of
        # missing strings was never actually shown to anyone.
        print('--- MISSES (%d) ---' % len(MISSES))
        for m in MISSES:
            print(m)
        sys.exit(1)


# Under a guard so that importing this module to reuse en_url()/PATH cannot
# rewrite eighteen Spanish pages as a side effect.
if __name__ == '__main__':
    main()
