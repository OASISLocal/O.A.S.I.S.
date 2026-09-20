/* Tooltip engine ------------------------------------------------------------
   Usage:  <span class="term" data-term="gguf">GGUF</span>
   Dictionary: tooltips.json (same source everywhere).
   Desktop: hover (180 ms delay). Keyboard: focus. Touch: tap to toggle.
   Escape closes. Fixed-positioned so it never shifts layout. */
(function () {
  var SCRIPT = document.currentScript;
  var BASE = SCRIPT && SCRIPT.src ? SCRIPT.src.replace(/assets\/tooltip\.js.*$/, '') : '';
  var TIP_ID = 'tt-live';
  var SHOW_DELAY = 180;
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var noHover = window.matchMedia && window.matchMedia('(hover: none)').matches;

  var data = null, tip = null, active = null, timer = null, pinned = false;

  function ensureTip() {
    if (tip) return tip;
    tip = document.createElement('div');
    tip.className = 'tt';
    tip.id = TIP_ID;
    tip.setAttribute('role', 'tooltip');
    document.body.appendChild(tip);
    return tip;
  }

  function place(el) {
    var r = el.getBoundingClientRect();
    var t = ensureTip();
    t.style.left = '0px';
    t.style.top = '0px';
    var w = t.offsetWidth, h = t.offsetHeight;
    var gap = 10, pad = 8;
    var left = r.left + r.width / 2 - w / 2;
    left = Math.max(pad, Math.min(left, window.innerWidth - w - pad));
    var top = r.top - h - gap;
    if (top < pad) top = r.bottom + gap;          // flip below when it doesn't fit
    t.style.left = Math.round(left) + 'px';
    t.style.top = Math.round(top) + 'px';
  }

  function show(el) {
    if (!data) return;
    var key = el.getAttribute('data-term');
    var entry = data[key];
    if (!entry) return;
    var t = ensureTip();
    t.textContent = '';
    var h = document.createElement('strong');
    h.className = 'tt-term';
    h.textContent = entry.label || key;
    t.appendChild(h);
    var p = document.createElement('p');
    p.className = 'tt-short';
    p.textContent = entry.short || '';
    t.appendChild(p);
    active = el;
    el.setAttribute('aria-describedby', TIP_ID);
    el.setAttribute('aria-expanded', 'true');
    t.classList.add('open');
    place(el);
  }

  function hide() {
    if (timer) { clearTimeout(timer); timer = null; }
    if (!tip) return;
    tip.classList.remove('open');
    if (active) {
      active.removeAttribute('aria-describedby');
      active.setAttribute('aria-expanded', 'false');
    }
    active = null;
    pinned = false;
  }

  function schedule(el) { timer = setTimeout(function () { show(el); }, SHOW_DELAY); }

  function wire(el) {
    if (el.getAttribute('data-tt-wired')) return;
    el.setAttribute('data-tt-wired', '1');
    el.setAttribute('tabindex', '0');
    el.setAttribute('role', 'button');
    el.setAttribute('aria-expanded', 'false');

    el.addEventListener('mouseenter', function () { if (!noHover && !pinned) schedule(el); });
    el.addEventListener('mouseleave', function () { if (!pinned) hide(); });
    el.addEventListener('focus', function () { show(el); });
    el.addEventListener('blur', function () { if (!pinned) hide(); });
    el.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter' || ev.key === ' ') {
        ev.preventDefault();
        if (active === el) hide(); else show(el);
      }
    });

    el.addEventListener('click', function (ev) {
      if (ev.target.closest && ev.target.closest('.tt')) return;   // let the link work
      if (noHover) {
        ev.preventDefault();
        if (active === el) { hide(); } else { pinned = false; show(el); pinned = true; }
      }
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && active) { var el = active; hide(); if (el.focus) el.focus(); }
  });
  document.addEventListener('click', function (e) {
    if (!pinned) return;
    if (tip && (tip.contains(e.target) || (active && active.contains(e.target)))) return;
    hide();
  });
  window.addEventListener('scroll', function () { if (active) place(active); }, { passive: true });
  window.addEventListener('resize', function () { if (active) place(active); });

  function scan() {
    var els = document.querySelectorAll('.term[data-term]');
    for (var i = 0; i < els.length; i++) wire(els[i]);
  }

  fetch(BASE + 'tooltips.json')
    .then(function (r) { return r.json(); })
    .then(function (json) { data = json; scan(); })
    .catch(function () { /* no dictionary: terms stay plain text */ });
}());
