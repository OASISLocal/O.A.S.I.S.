# -*- coding: utf-8 -*-
"""Subset the webfonts to what the site actually renders.

The six woff2 files shipped ~130 KB and none of them declared a unicode-range,
so every page downloaded the whole character set. Measured against the built
site: 45 pages render 113 distinct characters, and each font was carrying
225-230 glyphs, about 55% of which the site never draws.

The subset is the union of the Latin ranges the copy can contain and every
character the built site actually shows that the font has. That last part is the
important one: the site draws a few symbols (■ ▢ ★ ✓ ✕ ≠) that are not in the
Latin ranges, and a missing glyph is a visible empty box that no gate would
notice.

    python build_fonts.py            # subset assets/fonts/*.woff2 in place
    python build_fonts.py --check    # fail if a file is not subset (deploy gate)

Originals are kept as .orig beside each file on the first run, so a bad subset
can be undone without a git checkout.
"""
import glob, io, os, re, shutil, sys, collections

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(ROOT, "assets", "fonts")
SITE = os.path.join(ROOT, "_site")

# Latin + Latin-1 Supplement + Latin Extended-A + general punctuation (dashes,
# curly quotes, ellipsis) + the symbols and signs the copy uses.
BASE = (set(range(0x20, 0x7F)) | set(range(0xA0, 0x180)) |
        set(range(0x2000, 0x2070)) |
        set(range(0x20A0, 0x20C0)) |          # currency
        set(range(0x2100, 0x214F)) |          # letterlike: ™ ℃
        set(range(0x2190, 0x2195)) |          # arrows
        set(range(0x2200, 0x22FF)) |          # math: ≠ ≤ ≥
        set(range(0x25A0, 0x25FF)) |          # geometric: ■ ▢ ▲
        set(range(0x2600, 0x27BF)))           # misc symbols + dingbats: ★ ✓ ✕

ENTITIES = {
    "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'",
    "&nbsp;": " ", "&mdash;": "\u2014", "&ndash;": "\u2013",
    "&laquo;": "\u00ab", "&raquo;": "\u00bb", "&hellip;": "\u2026",
    "&middot;": "\u00b7", "&times;": "\u00d7", "&rarr;": "\u2192",
    "&larr;": "\u2190", "&trade;": "\u2122", "&copy;": "\u00a9",
    "&reg;": "\u00ae", "&deg;": "\u00b0", "&euro;": "\u20ac",
    "&plusmn;": "\u00b1", "&sup2;": "\u00b2", "&sup3;": "\u00b3",
    "&frac12;": "\u00bd", "&bull;": "\u2022", "&dagger;": "\u2020",
    "&prime;": "\u2032", "&Prime;": "\u2033", "&le;": "\u2264", "&ge;": "\u2265",
    "&ne;": "\u2260", "&infin;": "\u221e", "&check;": "\u2713",
    "&star;": "\u2605", "&cross;": "\u2715", "&square;": "\u25a1",
    "&sq;": "\u25a2", "&blackbox;": "\u25a0",
}


def visible_text(path):
    h = io.open(path, encoding="utf-8", errors="replace").read()
    h = re.sub(r"<(script|style)\b.*?</\1>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<!--.*?-->", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    for k, v in ENTITIES.items():
        h = h.replace(k, v)
    return h


def site_codepoints():
    cps = set()
    if os.path.isdir(SITE):
        for dp, _d, fs in os.walk(SITE):
            for f in fs:
                if f.endswith(".html"):
                    cps |= {ord(c) for c in visible_text(os.path.join(dp, f)) if ord(c) > 31}
    return cps


def target_set(font):
    """Everything the copy could contain, plus anything the site really draws."""
    cps = site_codepoints()
    have = set()
    for t in font["cmap"].tables:
        have |= set(t.cmap.keys())
    return (BASE | cps) & have, len(cps)


def process(name, write):
    path = os.path.join(FD, name)
    before = os.path.getsize(path)
    font = TTFont(path)
    cps, n_site = target_set(font)
    had = {x for t in font["cmap"].tables for x in t.cmap.keys()}
    font.close()

    # A character the site draws but the font never had is not a subsetting
    # problem: the browser already falls back to a system font for it. Only a
    # glyph the original had and the subset dropped is a regression.
    baseline = had
    orig = path + ".orig"
    if os.path.exists(orig):
        of = TTFont(orig)
        baseline = {x for t in of["cmap"].tables for x in t.cmap.keys()}
        of.close()
    site_cps = site_codepoints()
    lost = sorted(site_cps & baseline - cps)

    opts = subset.Options()
    opts.flavor = "woff2"
    opts.desubroutinize = True
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    opts.recalc_bounds = True
    opts.drop_tables = []

    src = path
    if not os.path.exists(path + ".orig") and os.path.getsize(path) > 0:
        shutil.copy2(path, path + ".orig")
    if os.path.exists(path + ".orig"):
        src = path + ".orig"

    sfont = subset.load_font(src, opts)
    subsetter = subset.Subsetter(options=opts)
    subsetter.populate(unicodes=cps)
    subsetter.subset(sfont)
    out = io.BytesIO()
    subset.save_font(sfont, out, opts)
    sfont.close()
    data = out.getvalue()

    after = len(data)
    if write:
        with open(path, "wb") as f:
            f.write(data)
    return before, after, len(cps), lost


def main():
    write = "--check" not in sys.argv
    rows = []
    problems = []
    for path in sorted(glob.glob(os.path.join(FD, "*.woff2"))):
        name = os.path.basename(path)
        before, after, n, lost = process(name, write)
        ok = (after <= before) if not write else True
        if not ok:
            problems.append("%s grew from %.1f to %.1f KB" % (name, before/1024, after/1024))
        if write:
            print("  %-26s %6.1f -> %5.1f KB  (-%.0f%%, %d glifos)"
                  % (name, before/1024, after/1024, 100.0*(before-after)/before, n))
        if lost:
            problems.append("%s dropped %d glyph(s) the site draws: %s"
                            % (name, len(lost),
                               " ".join("U+%04X" % c for c in lost[:8])))
        rows.append((name, before, after))

    if write and rows:
        tb = sum(r[1] for r in rows); ta = sum(r[2] for r in rows)
        print("  TOTAL                    %6.1f -> %5.1f KB  (-%.0f%%)"
              % (tb/1024, ta/1024, 100.0*(tb-ta)/tb))
    if problems:
        print("build_fonts: %d problema(s):" % len(problems))
        for p in problems:
            print("  x " + p)
        return 1
    if not write:
        print("build_fonts --check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
