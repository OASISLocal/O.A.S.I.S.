# -*- coding: utf-8 -*-
"""Where the site lives. One source of truth, read from _config.yml.

Nine scripts used to carry the domain written inside them: check_seo.py had six
references, translate-es-pages.ps1 three, build_es.py two, check_site.py two,
and one each in build_sitemap.py, build_glossary.py, build_news_sitemap.py and
sync-web.ps1. That is how the site ended up served from one host while its
canonicals, sitemap and hreflang pointed at another: the two had drifted.

_config.yml is already the canonical config, and Jekyll builds from it, so
nothing here is a new source of truth. It just stops the build tooling from
keeping a private copy of it.

    SITE     "https://oasislocal.github.io/O.A.S.I.S."   no trailing slash
    BASEURL  "/O.A.S.I.S./"                             with trailing slash
    PATH     the same, for hrefs written into static es/ pages, which have no
             front matter and therefore cannot use relative_url

_config.yml splits it in two: `url` is the host and `baseurl` is the path
prefix, so the absolute base is their sum, not either one alone.
"""
import io, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))


def _from_config(key):
    cfg = io.open(os.path.join(ROOT, "_config.yml"), encoding="utf-8").read()
    m = re.search(r'^%s:\s*"?([^"\n]+?)"?\s*$' % key, cfg, re.M)
    if not m:
        raise SystemExit("site_config: %r is not set in _config.yml" % key)
    return m.group(1).strip()


HOST = _from_config("url").rstrip("/")
BASEURL = _from_config("baseurl")
if not BASEURL.startswith("/"):
    BASEURL = "/" + BASEURL
if not BASEURL.endswith("/"):
    BASEURL += "/"
SITE = (HOST + BASEURL).rstrip("/")
PATH = BASEURL

if __name__ == "__main__":
    # Lets the PowerShell scripts read it instead of keeping their own copy:
    #   $site = python site_config.py SITE
    import sys
    key = sys.argv[1].upper() if len(sys.argv) > 1 else "SITE"
    values = {"SITE": SITE, "HOST": HOST, "BASEURL": BASEURL, "PATH": PATH}
    if key not in values:
        raise SystemExit("site_config: unknown key %r (have: %s)"
                         % (key, ", ".join(sorted(values))))
    print(values[key])
