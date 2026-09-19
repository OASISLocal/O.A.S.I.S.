/* Preview modes for testing the launch phases without deploying them.
   Home only. Query string: ?mode=teaser | ?mode=countdown[&date=ISO] | ?mode=live
   - Overlay is built by JS, so a no-JS visitor always sees the full site.
   - Countdown reads revealDate from launch.json (same source as sync-web.ps1);
     ?date=ISO overrides it. At zero it reveals the full site automatically.
   - This is a preview for testing, NOT a secret: the real HTML is still in
     view-source. For a real gate, deploy the teaser/countdown shells via sync-web.ps1. */
(function () {
  var q;
  try { q = new URLSearchParams(location.search); } catch (_) { return; }
  var mode = q.get('mode');
  if (mode !== 'teaser' && mode !== 'countdown') return;   // 'live' or absent: do nothing

  var SCRIPT = document.currentScript;
  var BASE = SCRIPT && SCRIPT.src ? SCRIPT.src.replace(/assets\/launch\.js.*$/, '') : '';
  var overlay = null, ticker = null;

  function lock(lock) {
    Array.prototype.forEach.call(
      document.querySelectorAll('header.top, main, footer, .sticky-cta'),
      function (el) { if (lock) el.setAttribute('inert', ''); else el.removeAttribute('inert'); }
    );
    document.body.style.overflow = lock ? 'hidden' : '';
  }

  function exitLink() {
    var a = document.createElement('a');
    a.href = location.pathname;                 // drop ?mode and ?date
    a.textContent = 'View full site';
    var p = document.createElement('p');
    p.className = 'launch-exit';
    p.appendChild(a);
    return p;
  }

  function build(label) {
    overlay = document.createElement('div');
    overlay.className = 'launch-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', label);
    var box = document.createElement('div');
    box.className = 'launch-box';
    overlay.appendChild(box);
    document.body.appendChild(overlay);
    lock(true);
    return box;
  }

  function nav(box) {
    var n = document.createElement('nav');
    var gh = document.createElement('a');
    gh.href = 'https://github.com/OASISLocal/O.A.S.I.S.';
    gh.target = '_blank'; gh.rel = 'noopener noreferrer'; gh.textContent = 'GitHub';
    var jr = document.createElement('a');
    jr.href = 'blog/'; jr.textContent = 'Journal';
    n.appendChild(gh); n.appendChild(jr);
    box.appendChild(n);
    box.appendChild(exitLink());
  }

  if (mode === 'teaser') {
    var tb = build('Teaser preview');
    tb.innerHTML = '<div class="mark" aria-hidden="true"></div>' +
      '<h2>Something local is coming.</h2>' +
      '<p>An AI assistant that lives on your PC — no cloud, no account. Watch this space, or follow along:</p>';
    nav(tb);
    return;
  }

  /* countdown */
  var cb = build('Countdown preview');
  cb.innerHTML = '<div class="mark" aria-hidden="true"></div>' +
    '<h2>O.A.S.I.S. — the reveal</h2><div class="cd" aria-live="polite"></div><p class="cd-date"></p>';
  nav(cb);
  var cd = cb.querySelector('.cd'), dd = cb.querySelector('.cd-date');

  function pad(n) { return (n < 10 ? '0' : '') + n; }

  function run(iso) {
    var target = new Date(iso || '');
    if (isNaN(target.getTime())) {
      cd.innerHTML = '<p>Date to be announced — watch the Journal.</p>';
      return;
    }
    dd.textContent = target.toUTCString() + '  ·  ' + target.toLocaleString();
    function tick() {
      var ms = target.getTime() - Date.now();
      if (ms <= 0) {                        // reveal
        if (ticker) clearInterval(ticker);
        lock(false);
        if (overlay) overlay.remove();
        return;
      }
      var s = Math.floor(ms / 1000);
      var d = Math.floor(s / 86400), h = Math.floor(s % 86400 / 3600),
          m = Math.floor(s % 3600 / 60), ss = s % 60;
      cd.innerHTML = '<div class="cd-grid" aria-hidden="true"><div><b>' + pad(d) + '</b><span>days</span></div>' +
        '<div><b>' + pad(h) + '</b><span>hours</span></div><div><b>' + pad(m) + '</b><span>min</span></div>' +
        '<div><b>' + pad(ss) + '</b><span>sec</span></div></div>';
    }
    tick();
    ticker = setInterval(tick, 1000);
  }

  var override = q.get('date');
  if (override) { run(override); return; }
  fetch(BASE + 'launch.json')
    .then(function (r) { return r.json(); })
    .then(function (j) { run(j && j.revealDate); })
    .catch(function () { run(''); });   // no launch.json: "to be announced"
}());
