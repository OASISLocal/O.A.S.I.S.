/* Language routing.
   - If the browser prefers Spanish and the visitor has not chosen a language,
     an English page redirects once to its Spanish twin (es/…).
   - The Spanish page then shows a notice with a link back to the English
     original, and remembers the choice either way.
   Client-side only: crawlers and no-JS visitors always get the English page. */
(function () {
  var STORE = 'oasis-lang';
  var root = document.documentElement;
  var lang = (root.getAttribute('lang') || 'en').toLowerCase().slice(0, 2);
  var path = location.pathname;
  var isES = /\/es\//.test(path) || /\/es$/.test(path);

  function pref() { try { return localStorage.getItem(STORE); } catch (_) { return null; } }
  function setPref(v) { try { localStorage.setItem(STORE, v); } catch (_) {} }

  // Explicit override in the URL: ?lang=en or ?lang=es (also used by tooling).
  var forced = (location.search.match(/[?&]lang=(en|es)(?:&|$)/) || [])[1];
  if (forced) setPref(forced);

  function twin(url, toES) {
    var m = url.match(/^(.*\/)([^\/]*)$/);
    var dir = m ? m[1] : '/', file = m ? m[2] : '';
    if (toES) return dir + 'es/' + file;
    // from /…/es/… back to the English root
    var esDir = dir.replace(/es\/([^\/]*\/)*$/, '');
    return (esDir + file) || '/';
  }

  // 1) English page: auto-redirect to Spanish when the browser prefers it.
  if (!isES && lang === 'en' && !pref()) {
    var skip = /(^|\/)404\.html$/.test(path) || /\/blog\//.test(path) || /\/launch\//.test(path);
    var primary = String((navigator.languages && navigator.languages[0]) || navigator.language || '').toLowerCase();
    if (!skip && primary.indexOf('es') === 0) {
      location.replace(twin(path, true) + '?lang=es');
      return;
    }
  }

  // 2) Spanish page reached by auto-redirect: explain and offer the original.
  if (isES && /(?:^|[?&])lang=es(?:&|$)/.test(location.search)) {
    var msg = (root.getAttribute('lang') || 'es').toLowerCase().slice(0, 2) === 'es';
    var bar = document.createElement('div');
    bar.className = 'lang-notice';
    bar.setAttribute('role', 'status');
    var text = document.createElement('span');
    text.className = 'ln-text';
    text.textContent = msg
      ? 'Le hemos mostrado la versión en español según el idioma de su navegador.'
      : 'We redirected you to the Spanish version based on your browser language.';
    var actions = document.createElement('span');
    actions.className = 'ln-actions';
    var en = document.createElement('a');
    en.className = 'ln-en';
    en.href = twin(path, false);
    en.lang = 'en';
    en.hreflang = 'en';
    en.textContent = msg ? 'Ver la original en inglés' : 'View the English original';
    var close = document.createElement('button');
    close.type = 'button';
    close.textContent = msg ? 'Quedarme en español' : 'Stay in Spanish';
    actions.appendChild(en);
    actions.appendChild(close);
    bar.appendChild(text);
    bar.appendChild(actions);
    document.body.appendChild(bar);
    en.addEventListener('click', function () { setPref('en'); });
    close.addEventListener('click', function () { setPref('es'); bar.remove(); });
    try { history.replaceState(null, '', path + (location.hash || '')); } catch (_) {}
  }

  // 3) Visible switcher: remember the explicit choice.
  Array.prototype.forEach.call(document.querySelectorAll('[data-lang-switch]'), function (a) {
    a.addEventListener('click', function () { setPref(a.getAttribute('data-lang-switch')); });
  });
}());
