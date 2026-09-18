/* OASIS web — shared bits: theme + mobile nav. No trackers. */
(function () {
  var root = document.documentElement, btn = document.getElementById('theme-btn');
  function paint(t) {
    root.setAttribute('data-theme', t);
    if (btn) btn.textContent = (t === 'light') ? 'Dark' : 'Light';
    try { localStorage.setItem('oasis-theme', t); } catch (_) {}
  }
  var saved = null;
  try { saved = localStorage.getItem('oasis-theme'); } catch (_) {}
  paint(saved === 'light' || saved === 'dark' ? saved : 'dark');
  if (btn) btn.addEventListener('click', function () {
    paint(root.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
  });
  var burger = document.getElementById('burger'), mnav = document.getElementById('mnav');
  if (burger && mnav) {
    burger.addEventListener('click', function () {
      var open = mnav.classList.toggle('open');
      burger.setAttribute('aria-expanded', String(open));
    });
    mnav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { mnav.classList.remove('open'); });
    });
  }
}());
