# Google News — prepared, not activated

**Status: dormant.** Everything needed to appear in Google News is built and
sitting in the repository, but nothing is switched on. This file is the
runbook; nothing below has been executed.

## What is already in place

| Piece | File | State |
|---|---|---|
| RSS 2.0 feed (Google News does not accept Atom) | `blog/rss.xml` → `/blog/rss.xml` | built, **not linked from any page** |
| Atom feed (existing) | `blog/feed.xml` → `/blog/feed.xml` | live, linked from the blog layout |
| News sitemap generator | `build_news_sitemap.py` | built, **not referenced from robots.txt** |
| News sitemap output | `news-sitemap.xml` | generated with 0 articles until one is published in the window |
| Toggle | `ACTIVATED = False` in `build_news_sitemap.py` | off |

## How Google News actually works (the parts that surprise people)

1. **It is a stream, not an archive.** A news sitemap may only contain articles
   from the last **~48 hours**. Anything older is ignored, and the file is
   supposed to be regenerated on every publish. `build_news_sitemap.py` keeps a
   2-day window (`WINDOW_DAYS = 2`) and drops everything else.
2. **Every article needs a real publication date** inside that window. Articles
   published three days ago will never appear, no matter how good they are.
3. **It is not a ranking shortcut.** Google News decides what is newsworthy. A
   technical explainer rarely makes the "Top Stories", but it can appear in
   Google News search results and in the "For you" feed.
4. **You need a verified Publisher Center.** Without it, the news sitemap is
   ignored. Verification is manual and takes a couple of days (adding a logo
   file, a publication name and contact e-mail to
   `news.google.com/publisher-center`).
5. **Editorial quality still applies.** Clickbait or rewritten-away articles get
   filtered; the Journal's tone (no adjectives, honest) is an asset here, not a
   handicap.

## Activation checklist (do it in this order, by hand)

- [ ] 1. Publish at least one real article, then wait until it is inside the
      48-hour window. `python build_news_sitemap.py --missing` must report
      `articles inside the 2-day window: 1` or more.
- [ ] 2. Register and verify the domain in Google News Publisher Center
      (`OASISLocal/O.A.S.I.S.`). Set the publication name to the one used in
      `build_news_sitemap.py` (`PUBLICATION`).
- [ ] 3. Set `ACTIVATED = True` in `build_news_sitemap.py`.
- [ ] 4. Add the news sitemap to `robots.txt`:
      `Sitemap: https://oasislocal.github.io/O.A.S.I.S./news-sitemap.xml`
      (only from this step on; until then Google is not told about it).
- [ ] 5. Advertise the RSS feed. Google News also picks up RSS, so this one line
      is worth adding to `_layouts/default.html` (and it is useful for humans):
      `<link rel="alternate" type="application/rss+xml" title="O.A.S.I.S. Journal" href="/blog/rss.xml">`
- [ ] 6. Submit `news-sitemap.xml` and `blog/rss.xml` in Google Search Console.
- [ ] 7. From then on, `sync-web.ps1` regenerates both feeds on every publish
      (see the "news" step below).

## Making it automatic (still dormant)

`sync-web.ps1` does **not** call `build_news_sitemap.py` yet. When activation
happens, add to the commit phase, before the sitemap check:

```powershell
python build_news_sitemap.py
```

and to the checks phase:

```powershell
python build_news_sitemap.py --check
```

Until then the news sitemap is a file that can go stale, which is exactly why it
is not referenced from `robots.txt`: Google has no reason to look at it.

## Rehearsal

`python build_news_sitemap.py --missing` prints the state of the toggle, the
number of articles currently inside the window, and the activation steps. That
is the command to run before deciding to switch it on.
