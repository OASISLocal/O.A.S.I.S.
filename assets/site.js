/* OASIS web — shared bits: theme + mobile nav. No trackers. */
(function () {
  var root = document.documentElement, btn = document.getElementById('theme-btn');
  function paint(t) {
    root.setAttribute('data-theme', t);
    if (btn) {
      btn.textContent = (t === 'light') ? 'Dark' : 'Light';
      btn.setAttribute('aria-label', t === 'light' ? 'Switch to dark mode' : 'Switch to light mode');
    }
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = (t === 'light') ? '#f7f7f5' : '#111111';
    try { localStorage.setItem('oasis-theme', t); } catch (_) {}
  }
  var saved = null;
  try { saved = localStorage.getItem('oasis-theme'); } catch (_) {}
  paint(saved === 'light' || saved === 'dark' ? saved : 'dark');
  if (btn) btn.addEventListener('click', function () {
    paint(root.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
  });
  /* Mobile menu: rebuilt from the desktop nav on every load, so the two
     can never drift apart. Download + GitHub are appended (not in desktop nav). */
  var burger = document.getElementById('burger'), mnav = document.getElementById('mnav');
  if (burger && mnav) {
    var src = document.querySelector('.top nav.links');
    mnav.innerHTML = '';
    if (src) {
      Array.prototype.forEach.call(src.querySelectorAll('a'), function (a) {
        var c = a.cloneNode(true);
        c.removeAttribute('aria-current');
        mnav.appendChild(c);
      });
    }
    var dl = document.createElement('a');
    dl.href = 'download.html'; dl.textContent = 'Download';
    mnav.appendChild(dl);
    burger.addEventListener('click', function () {
      var open = mnav.classList.toggle('open');
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      if (open) {
        var first = mnav.querySelector('a');
        if (first) first.focus();
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mnav.classList.contains('open')) {
        mnav.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
        burger.setAttribute('aria-label', 'Open menu');
        burger.focus();
      }
    });
    mnav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        mnav.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
        burger.setAttribute('aria-label', 'Open menu');
      });
    });
    document.addEventListener('click', function (e) {
      if (!mnav.classList.contains('open') || mnav.contains(e.target) || burger.contains(e.target)) return;
      mnav.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
      burger.setAttribute('aria-label', 'Open menu');
    });
  }
}());
