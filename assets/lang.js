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

  // Explicit override in the URL: ?lang=en | ?lang=es (force) or ?lang=auto (re-detect).
  var forced = (location.search.match(/[?&]lang=(en|es|auto)(?:&|$)/) || [])[1];
  if (forced === 'en' || forced === 'es') { setPref(forced); }
  else if (forced === 'auto') { try { localStorage.removeItem(STORE); } catch (_) {} }

  /* Does the visitor want Spanish? Signals, in order:
     browser preference (primary, then the next two) and, when the primary is
     not English, the time zone of a Spanish-speaking region. All client-side:
     no IP lookup, no request. */
  var ES_TZ = /(Europe\/Madrid|Atlantic\/Canary|Africa\/Ceuta|Africa\/Malabo|America\/(Mexico_City|Monterrey|Hermosillo|Chihuahua|Mazatlan|Bahia_Banderas|Merida|Matamoros|Ojinaga|Tijuana|Bogota|Lima|Santiago|Argentina|Caracas|Guayaquil|Montevideo|Panama|Guatemala|Tegucigalpa|El_Salvador|Managua|Costa_Rica|Havana|Santo_Domingo|Puerto_Rico|Asuncion|La_Paz|Curacao|Aruba))/i;
  function wantsSpanish() {
    var list = (navigator.languages && navigator.languages.length) ? navigator.languages : [navigator.language || ''];
    var primary = String(list[0] || '').toLowerCase();
    if (primary.indexOf('es') === 0) return true;
    if (primary.indexOf('en') === 0) return false;          // English-first visitors stay in English
    for (var i = 1; i < Math.min(list.length, 3); i++) {
      if (String(list[i]).toLowerCase().indexOf('es') === 0) return true;
    }
    try {
      var tz = (Intl.DateTimeFormat().resolvedOptions().timeZone || '');
      if (ES_TZ.test(tz)) return true;                      // region signal
    } catch (_) {}
    return false;
  }

  function twin(url, toES) {
    var m = url.match(/^(.*\/)([^\/]*)$/);
    var dir = m ? m[1] : '/', file = m ? m[2] : '';
    if (toES) return dir + 'es/' + file;
    // from /…/es/… back to the English root
    var esDir = dir.replace(/es\/([^\/]*\/)*$/, '');
    return (esDir + file) || '/';
  }

  /* 0) An explicit choice is sticky, in both directions.

     This is the safety net for the language. Every link in the layout now
     carries the /es/ prefix, so it should never be needed -- but a link that
     slips through (a hand-written one in a page, a bookmark, a search result)
     used to drop the reader into the other language and keep them there, because
     the redirect below only fired when there was no stored preference. The
     server declares the twin with <link rel="alternate" hreflang>, so trust that
     and only redirect when it is actually there. */
  var stored = pref();
  if (stored && ((stored === 'es') !== isES)) {
    var want = document.querySelector('link[rel="alternate"][hreflang="' + stored + '"]');
    var to = want && want.getAttribute('href');
    if (to && to !== path) {
      location.replace(to);
      return;
    }
  }

  // 1) English page: auto-redirect to Spanish when the browser prefers it.
  if (!isES && lang === 'en' && !pref()) {
    var skip = /(^|\/)404\.html$/.test(path) || /\/launch\//.test(path);
    var underBlog = /\/blog(\/|$)/.test(path);
    var altEs = document.querySelector('link[rel="alternate"][hreflang="es"]');
    if (!skip && wantsSpanish()) {
      var target = null;
      if (altEs) { target = altEs.getAttribute('href'); }          // explicit Spanish twin (blog posts, legal…)
      else if (!underBlog) { target = twin(path, true); }          // mechanical /es/ twin
      if (target) {
        location.replace(target + (target.indexOf('?') >= 0 ? '&' : '?') + 'lang=es');
        return;
      }
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
    var altEn = document.querySelector('link[rel="alternate"][hreflang="en"]');
    en.href = altEn ? altEn.getAttribute('href') : twin(path, false);
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
