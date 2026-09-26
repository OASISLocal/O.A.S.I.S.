# -*- coding: utf-8 -*-
"""Give every page a Content-Security-Policy that matches what the site does.

The site makes a promise in its own privacy policy: no analytics, no pixels, no
third-party SDK, fonts and assets served from here. That promise was a claim in
prose. A CSP is what turns it into something the browser enforces, so a future
snippet that quietly reaches for a third party fails loudly instead of shipping.

The policy is deliberately as tight as the site can actually live with:

  default-src 'self'   nothing loads unless it is listed below
  connect-src           the only two things the site ever asks for: the public
                        GitHub API for the star count, and the Cloudflare Worker
                        that receives a waitlist signup
  frame-src             the video component only builds an iframe after a click,
                        and only for these two providers
  img-src 'self' data:  local images plus inline data URIs; nothing is hotlinked
  object-src 'none'    no plugins, ever

'script-src' and 'style-src' need 'unsafe-inline' and it is worth being clear
about why rather than pretending otherwise: the built site carries 81 inline
<script> blocks and 123 style="" attributes, and a static Jekyll build cannot
mint a per-response nonce, so a nonce-based policy is not available here. What
the policy still buys is that a third-party origin cannot be added to either
directive, which is the failure that actually happens by accident.

A <meta> CSP cannot carry frame-ancestors, report-uri or sandbox: those are
header-only. GitHub Pages does not let this project set response headers, so
those three stay out of scope and clickjacking is not covered by this file.

    python build_csp.py            # inject the meta tag where it is missing
    python build_csp.py --check    # fail if a page has no policy (deploy gate)
"""
import glob, io, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))

POLICY = "; ".join([
    "default-src 'self'",
    "base-uri 'self'",
    "object-src 'none'",
    "script-src 'self' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "font-src 'self'",
    "connect-src 'self' https://api.github.com "
    "https://oasis-waitlist.sanitariorteba.workers.dev",
    "frame-src https://www.youtube-nocookie.com https://player.vimeo.com",
    "form-action 'self'",
])
TAG = '<meta http-equiv="Content-Security-Policy" content="%s">' % POLICY

# Front-matter pages are rendered through _layouts, so the policy belongs in the
# layout and injecting it into the .md/.html source would do nothing. Static
# pages carry their own <head> and need it in the file.
SKIP_DIRS = ("_site", "_layouts", "_includes", "_posts", "blog", "launch",
             "production", "node_modules", ".git")


def targets():
    """Every file that ends up as a page: the static roots plus the layouts."""
    found = []
    for pattern in ("*.html", "es/*.html", "_layouts/*.html"):
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            rel = os.path.relpath(path, ROOT)
            if rel.split(os.sep)[0] in SKIP_DIRS and not rel.startswith("_layouts"):
                continue
            found.append(path)
    return found


def has_policy(html):
    return "Content-Security-Policy" in html


def dominant_newline(html):
    """Match the file we are editing. Git stores this repo as LF and hands the
    working copy CRLF, so writing a bare \\n into a CRLF file leaves it mixed:
    a one-line diff becomes a file whose line endings disagree with itself, and
    that is the kind of noise that hides a real change in review."""
    crlf = html.count("\r\n")
    lf = html.count("\n") - crlf
    return "\r\n" if crlf > lf else "\n"


def inject(html):
    """Put the meta first thing in <head>. A policy that arrives after the
    stylesheet or a script has already been fetched applies too late to stop it,
    so position matters as much as presence."""
    if has_policy(html):
        return html, False
    nl = dominant_newline(html)
    out, n = re.subn(r"(<head\b[^>]*>)",
                     lambda m: m.group(1) + nl + TAG, html, count=1)
    if not n:
        return html, False
    return out, True


def main():
    check = "--check" in sys.argv
    patched, skipped, problems = [], [], []

    for path in targets():
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        html = io.open(path, encoding="utf-8", newline="").read()
        if has_policy(html):
            continue
        if "<head" not in html:
            skipped.append(rel)
            continue
        new, changed = inject(html)
        if not changed:
            problems.append("%s: tiene <head> pero no se pudo insertar la meta" % rel)
            continue
        if check:
            patched.append(rel)
        else:
            io.open(path, "w", encoding="utf-8", newline="").write(new)
            patched.append(rel)

    if skipped:
        # Not an error: a page without a <head> of its own gets the policy from
        # its layout. Listed so a surprise is visible rather than silent.
        print("build_csp: sin <head> propio, lo cubren los layouts: %s"
              % ", ".join(skipped))

    if problems:
        print("build_csp: %d problema(s):" % len(problems))
        for p in problems:
            print("  x " + p)
        return 1

    if check:
        if patched:
            print("build_csp --check: %d pagina(s) sin CSP: %s"
                  % (len(patched), ", ".join(patched)))
            print(" Ejecuta: python build_csp.py")
            return 1
        print("build_csp --check: OK (%d paginas con politica)"
              % len(targets()))
        return 0

    if patched:
        print("build_csp: CSP anadido a %d pagina(s)" % len(patched))
        for p in patched:
            print("  + " + p)
    else:
        print("build_csp: todas las paginas tienen politica")
    return 0


if __name__ == "__main__":
    sys.exit(main())
