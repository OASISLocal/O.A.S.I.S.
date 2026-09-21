/* OASIS web — shared bits: theme + mobile nav. No trackers. Bilingual (en/es). */
(function () {
  var ES = (document.documentElement.getAttribute('lang') || 'en').toLowerCase().indexOf('es') === 0;
  var S = ES ? {
    light: 'Claro', dark: 'Oscuro',
    toDark: 'Cambiar a modo oscuro', toLight: 'Cambiar a modo claro',
    open: 'Abrir menú', close: 'Cerrar menú',
    download: 'Descargar', blog: 'Blog'
  } : {
    light: 'Light', dark: 'Dark',
    toDark: 'Switch to dark mode', toLight: 'Switch to light mode',
    open: 'Open menu', close: 'Close menu',
    download: 'Download', blog: 'Blog'
  };
  var root = document.documentElement, btn = document.getElementById('theme-btn');
  function paint(t) {
    root.setAttribute('data-theme', t);
    if (btn) {
      btn.textContent = (t === 'light') ? S.dark : S.light;
      btn.setAttribute('aria-label', t === 'light' ? S.toDark : S.toLight);
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
    var src = document.querySelector('.top nav.links') || document.querySelector('.mast nav.links');
    mnav.innerHTML = '';
    if (src) {
      Array.prototype.forEach.call(src.querySelectorAll('a'), function (a) {
        var c = a.cloneNode(true);
        c.removeAttribute('aria-current');
        mnav.appendChild(c);
      });
    }
    var dl = document.createElement('a');
    dl.href = ES ? 'download.html' : 'download.html'; dl.textContent = S.download;
    mnav.appendChild(dl);
    burger.addEventListener('click', function () {
      var open = mnav.classList.toggle('open');
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? S.close : S.open);
      if (open) {
        var first = mnav.querySelector('a');
        if (first) first.focus();
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mnav.classList.contains('open')) {
        mnav.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
        burger.setAttribute('aria-label', S.open);
        burger.focus();
      }
    });
    Array.prototype.forEach.call(mnav.querySelectorAll('a'), function (a) {
      a.addEventListener('click', function () {
        mnav.classList.remove('open');
        burger.setAttribute('aria-expanded', 'false');
        burger.setAttribute('aria-label', S.open);
      });
    });
  }
}());
