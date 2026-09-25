/* components.js — behaviour for the Journal components.
 *
 * One file, no dependencies, no third-party requests. Every component degrades:
 * with this file blocked, callouts, tables, details, timelines and tabs still
 * render and still work, because the markup is real HTML.
 *
 * Loaded only on pages that use a component (see _layouts/post.html).
 */
(function () {
  "use strict";

  var doc = document;

  /* ------------------------------------------------------------ callouts
   * Nothing to initialise: the only job is to make the type visible as a word,
   * not only as a colour, and that is already in the markup.
   */

  /* --------------------------------------------------------------- tables
   * Sortable headers. The values are compared numerically when every cell in
   * the column looks like a number, and as text otherwise.
   */
  function initTables() {
    // The class is normally already in the markup, so the layout rules work
    // before this script runs. The template only carries the sort options, and
    // anything the author omitted is filled in here.
    var wraps = doc.querySelectorAll("[data-cmp-table-config]");
    Array.prototype.forEach.call(wraps, function (tpl) {
      var parts = (tpl.textContent || "").split("|");
      var table = tpl.parentNode.querySelector("table");
      if (!table) return;
      var want = (parts[0] || "").trim();
      if (want && !table.className) {
        table.className = want;
      }
      if (parts[1] === "true") table.setAttribute("data-sortable", "true");
      var presort = (parts[2] || "").trim();
      if (presort) {
        var heads = table.querySelectorAll("thead th");
        for (var i = 0; i < heads.length; i++) {
          if ((heads[i].getAttribute("data-key") || "").toLowerCase() === presort.toLowerCase()) {
            setTimeout(function (h) { sortBy(table, h); }(heads[i]), 0);
            break;
          }
        }
      }
    });
    initSortableTables();
  }

  /* Turn the <th data-sort> headers into buttons. */
  function initSortableTables() {
    var tables = doc.querySelectorAll("[data-cmp-table]");
    Array.prototype.forEach.call(tables, function (table) {
      var heads = table.querySelectorAll("thead th[data-sort]");
      Array.prototype.forEach.call(heads, function (th) {
        if (th.querySelector("button")) return;
        var btn = doc.createElement("button");
        btn.type = "button";
        btn.textContent = th.textContent.trim();
        th.textContent = "";
        th.appendChild(btn);
        th.setAttribute("aria-sort", "none");
        btn.addEventListener("click", function () { sortBy(table, th); });
      });
    });
  }

  function cellValue(row, index) {
    var cell = row.cells[index];
    if (!cell) return "";
    return (cell.getAttribute("data-value") || cell.textContent || "").trim();
  }

  function isNumericColumn(table, index) {
    var rows = table.tBodies[0] ? table.tBodies[0].rows : [];
    var seen = 0, numeric = 0;
    for (var i = 0; i < rows.length; i++) {
      var v = cellValue(rows[i], index);
      if (!v) continue;
      seen++;
      if (/^-?\d+([.,]\d+)?\s*[a-zA-Z%€$]*$/.test(v.replace(/\s/g, ""))) numeric++;
    }
    return seen > 0 && numeric / seen >= 0.8;
  }

  function sortBy(table, th) {
    var index = Array.prototype.indexOf.call(th.parentNode.cells, th);
    var body = table.tBodies[0];
    if (!body) return;
    var current = th.getAttribute("aria-sort");
    var asc = current !== "ascending";
    var numeric = isNumericColumn(table, index);

    var rows = Array.prototype.slice.call(body.rows);
    rows.sort(function (a, b) {
      var va = cellValue(a, index), vb = cellValue(b, index);
      if (numeric) {
        var na = parseFloat(va.replace(/,/g, ".").replace(/[^\d.\-]/g, ""));
        var nb = parseFloat(vb.replace(/,/g, ".").replace(/[^\d.\-]/g, ""));
        if (isNaN(na) && isNaN(nb)) return 0;
        if (isNaN(na)) return 1;
        if (isNaN(nb)) return -1;
        return asc ? na - nb : nb - na;
      }
      return asc ? va.localeCompare(vb) : vb.localeCompare(va);
    });

    var frag = doc.createDocumentFragment();
    rows.forEach(function (r) { frag.appendChild(r); });
    body.appendChild(frag);

    Array.prototype.forEach.call(th.parentNode.cells, function (c) {
      if (c !== th) c.setAttribute("aria-sort", "none");
    });
    th.setAttribute("aria-sort", asc ? "ascending" : "descending");
  }

  /* -------------------------------------------------------------- details
   * Only the "expand all" control. <details> already works alone.
   */
  function initDetails() {
    var groups = doc.querySelectorAll("[data-cmp-details]");
    Array.prototype.forEach.call(groups, function (group) {
      var items = group.querySelectorAll("details");
      if (!items.length || group.querySelector(".cmp-details__toggle")) return;

      var bar = doc.createElement("div");
      bar.className = "cmp-details__toggle";
      var open = doc.createElement("button");
      open.type = "button";
      open.textContent = group.getAttribute("data-open-label") || "Expand all";
      var close = doc.createElement("button");
      close.type = "button";
      close.textContent = group.getAttribute("data-close-label") || "Collapse all";
      open.addEventListener("click", function () {
        Array.prototype.forEach.call(items, function (d) { d.open = true; });
      });
      close.addEventListener("click", function () {
        Array.prototype.forEach.call(items, function (d) { d.open = false; });
      });
      bar.appendChild(open);
      bar.appendChild(close);
      group.insertBefore(bar, group.firstChild);
    });
  }

  /* ---------------------------------------------------------------- video
   * The iframe is created on click, so a post with three videos makes zero
   * third-party requests until the reader asks for one.
   */
  function initVideo() {
    var facades = doc.querySelectorAll("[data-cmp-video]");
    Array.prototype.forEach.call(facades, function (facade) {
      var btn = facade.querySelector("[data-cmp-video-play]");
      if (!btn) return;
      btn.addEventListener("click", function () {
        var id = facade.getAttribute("data-video-id");
        var provider = facade.getAttribute("data-video-provider") || "youtube";
        var src;
        if (provider === "vimeo") {
          src = "https://player.vimeo.com/video/" + id + "?autoplay=1&dnt=1";
        } else {
          src = "https://www.youtube-nocookie.com/embed/" + id +
                "?autoplay=1&rel=0&modestbranding=1";
        }
        var iframe = doc.createElement("iframe");
        iframe.className = "cmp-video__iframe";
        iframe.src = src;
        iframe.title = facade.getAttribute("data-video-title") || "Video";
        iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
        iframe.allowFullscreen = true;
        iframe.loading = "lazy";
        iframe.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
        facade.innerHTML = "";
        facade.appendChild(iframe);
        iframe.focus();
      });
    });
  }

  /* -------------------------------------------------------------- gallery
   * A small lightbox. One overlay for the whole page, arrow keys, Escape,
   * and focus returned to the thumbnail that opened it.
   */
  var lightbox = null, lightboxIndex = 0, lastFocused = null, galleryItems = [];

  function buildLightbox() {
    if (lightbox) return;
    lightbox = doc.createElement("div");
    lightbox.className = "cmp-lightbox";
    lightbox.setAttribute("role", "dialog");
    lightbox.setAttribute("aria-modal", "true");
    lightbox.hidden = true;
    lightbox.innerHTML =
      '<div class="cmp-lightbox__bar">' +
      '<span data-cmp-lb-counter></span>' +
      '<button type="button" class="cmp-lightbox__close" data-cmp-lb-close>Close (Esc)</button>' +
      "</div>" +
      '<div class="cmp-lightbox__stage">' +
      '<button type="button" class="cmp-lightbox__nav cmp-lightbox__nav--prev" ' +
      'data-cmp-lb-prev aria-label="Previous image">&#8592;</button>' +
      '<img class="cmp-lightbox__image" data-cmp-lb-image alt="">' +
      '<button type="button" class="cmp-lightbox__nav cmp-lightbox__nav--next" ' +
      'data-cmp-lb-next aria-label="Next image">&#8594;</button>' +
      "</div>" +
      '<p class="cmp-lightbox__caption" data-cmp-lb-caption></p>';
    doc.body.appendChild(lightbox);

    lightbox.querySelector("[data-cmp-lb-close]").addEventListener("click", closeLightbox);
    lightbox.querySelector("[data-cmp-lb-prev]").addEventListener("click", function () { step(-1); });
    lightbox.querySelector("[data-cmp-lb-next]").addEventListener("click", function () { step(1); });
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox || e.target.classList.contains("cmp-lightbox__stage")) {
        closeLightbox();
      }
    });
    doc.addEventListener("keydown", function (e) {
      if (lightbox.hidden) return;
      if (e.key === "Escape") { e.preventDefault(); closeLightbox(); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); step(-1); }
      else if (e.key === "ArrowRight") { e.preventDefault(); step(1); }
      else if (e.key === "Tab") trapFocus(e);
    });
  }

  function trapFocus(e) {
    var focusables = lightbox.querySelectorAll("button");
    if (!focusables.length) return;
    var first = focusables[0], last = focusables[focusables.length - 1];
    if (e.shiftKey && doc.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && doc.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  function showLightbox(index) {
    buildLightbox();
    galleryItems = Array.prototype.slice.call(doc.querySelectorAll("[data-cmp-gallery-item]"));
    if (!galleryItems.length) return;
    lightboxIndex = (index + galleryItems.length) % galleryItems.length;
    var item = galleryItems[lightboxIndex];
    var img = item.querySelector("img");
    var cap = item.getAttribute("data-caption") || "";
    lightbox.querySelector("[data-cmp-lb-image]").src = img.getAttribute("data-full") || img.src;
    lightbox.querySelector("[data-cmp-lb-image]").alt = img.alt || "";
    lightbox.querySelector("[data-cmp-lb-caption]").textContent = cap;
    lightbox.querySelector("[data-cmp-lb-counter]").textContent =
      (lightboxIndex + 1) + " / " + galleryItems.length;
    lightbox.hidden = false;
    doc.body.style.overflow = "hidden";
    lightbox.querySelector("[data-cmp-lb-close]").focus();
  }

  function closeLightbox() {
    if (!lightbox || lightbox.hidden) return;
    lightbox.hidden = true;
    doc.body.style.overflow = "";
    if (lastFocused) lastFocused.focus();
  }

  function step(dir) {
    showLightbox(lightboxIndex + dir);
  }

  function initGallery() {
    var buttons = doc.querySelectorAll("[data-cmp-gallery-open]");
    Array.prototype.forEach.call(buttons, function (btn) {
      btn.addEventListener("click", function () {
        lastFocused = btn;
        showLightbox(parseInt(btn.getAttribute("data-index"), 10) || 0);
      });
    });
  }

  /* ----------------------------------------------------------------- tabs
   * Follows the WAI-ARIA tabs pattern: one tab stop, arrows to move.
   */
  function initTabs() {
    var groups = doc.querySelectorAll("[data-cmp-tabs]");
    Array.prototype.forEach.call(groups, function (group) {
      var tabs = group.querySelectorAll('[role="tab"]');
      var panels = group.querySelectorAll('[role="tabpanel"]');
      if (!tabs.length) return;

      function select(index, focus) {
        Array.prototype.forEach.call(tabs, function (t, i) {
          var on = i === index;
          t.setAttribute("aria-selected", on ? "true" : "false");
          t.tabIndex = on ? 0 : -1;
          if (on && focus) t.focus();
        });
        Array.prototype.forEach.call(panels, function (p, i) {
          p.hidden = i !== index;
        });
      }

      Array.prototype.forEach.call(tabs, function (tab, i) {
        tab.addEventListener("click", function () { select(i, false); });
        tab.addEventListener("keydown", function (e) {
          var n = null;
          if (e.key === "ArrowRight") n = (i + 1) % tabs.length;
          else if (e.key === "ArrowLeft") n = (i - 1 + tabs.length) % tabs.length;
          else if (e.key === "Home") n = 0;
          else if (e.key === "End") n = tabs.length - 1;
          if (n !== null) { e.preventDefault(); select(n, true); }
        });
      });
      select(0, false);
    });
  }

  /* ---------------------------------------------------------------- charts
   * The numbers come from a <table> in the markup; the SVG is drawn from that
   * table. No data is hard-coded here, so the visible chart and the readable
   * table can never disagree.
   */
  var NS = "http://www.w3.org/2000/svg";

  function el(name, attrs) {
    var node = doc.createElementNS(NS, name);
    for (var k in attrs) if (attrs.hasOwnProperty(k)) node.setAttribute(k, attrs[k]);
    return node;
  }

  function readData(chart) {
    var table = chart.querySelector(".cmp-chart__data table");
    if (!table) return null;
    var body = table.querySelector("tbody") || table.tBodies[0];
    if (!body) return null;
    var rows = Array.prototype.slice.call(body.rows);
    var labels = [], values = [];
    rows.forEach(function (row) {
      var c0 = row.cells[0], c1 = row.cells[1];
      if (!c0 || !c1) return;
      labels.push(c0.textContent.trim());
      values.push(parseFloat(c1.getAttribute("data-value") || c1.textContent));
    });
    return {
      labels: labels,
      values: values,
      unit: chart.getAttribute("data-unit") || ""
    };
  }

  function niceMax(v) {
    if (v <= 0) return 1;
    var mag = Math.pow(10, Math.floor(Math.log10(v)));
    var n = v / mag;
    var step = n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10;
    return step * mag;
  }

  function drawBar(chart, data) {
    var W = 640, H = 260, padL = 44, padR = 12, padT = 12, padB = 34;
    var iw = W - padL - padR, ih = H - padT - padB;
    var max = niceMax(Math.max.apply(null, data.values) * 1.1);
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "presentation" });
    var band = iw / data.values.length;

    for (var g = 0; g <= 4; g++) {
      var y = padT + ih - (ih * g / 4);
      svg.appendChild(el("line", { class: "grid", x1: padL, x2: W - padR, y1: y, y2: y }));
      var t = el("text", { class: "tick tick--y", x: padL - 6, y: y + 3 });
      t.textContent = fmt(max * g / 4) + data.unit;
      svg.appendChild(t);
    }

    data.values.forEach(function (v, i) {
      var h = Math.max(1, (v / max) * ih);
      var x = padL + i * band + band * 0.18;
      var w = band * 0.64;
      var y = padT + ih - h;
      var bar = el("rect", { class: "bar", x: x, y: y, width: w, height: h });
      bar.appendChild(el("title", {})).textContent =
        data.labels[i] + ": " + fmt(v) + data.unit;
      svg.appendChild(bar);
      var lab = el("text", { class: "tick tick--x", x: x + w / 2, y: H - 12 });
      lab.textContent = data.labels[i];
      svg.appendChild(lab);
      var val = el("text", { class: "cmp-chart__value", x: x + w / 2, y: y - 5 });
      val.textContent = fmt(v) + data.unit;
      svg.appendChild(val);
    });

    svg.appendChild(el("line", { class: "axis", x1: padL, x2: W - padR, y1: padT + ih, y2: padT + ih }));
    return svg;
  }

  function drawLine(chart, data) {
    var W = 640, H = 260, padL = 44, padR = 14, padT = 14, padB = 34;
    var iw = W - padL - padR, ih = H - padT - padB;
    var max = niceMax(Math.max.apply(null, data.values) * 1.1);
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "presentation" });
    var stepX = data.values.length > 1 ? iw / (data.values.length - 1) : 0;

    for (var g = 0; g <= 4; g++) {
      var y = padT + ih - (ih * g / 4);
      svg.appendChild(el("line", { class: "grid", x1: padL, x2: W - padR, y1: y, y2: y }));
      var t = el("text", { class: "tick tick--y", x: padL - 6, y: y + 3 });
      t.textContent = fmt(max * g / 4) + data.unit;
      svg.appendChild(t);
    }

    var pts = data.values.map(function (v, i) {
      return [padL + i * stepX, padT + ih - (v / max) * ih];
    });
    if (pts.length > 1) {
      var area = "M" + pts[0][0] + "," + (padT + ih) +
        pts.map(function (p) { return "L" + p[0] + "," + p[1]; }).join("") +
        "L" + pts[pts.length - 1][0] + "," + (padT + ih) + "Z";
      svg.appendChild(el("path", { class: "area", d: area }));
      svg.appendChild(el("path", { class: "line", d: "M" + pts.map(function (p) {
        return p[0] + "," + p[1];
      }).join("L") }));
    }
    pts.forEach(function (p, i) {
      var dot = el("circle", { class: "dot", cx: p[0], cy: p[1], r: 3.5 });
      dot.appendChild(el("title", {})).textContent =
        data.labels[i] + ": " + fmt(data.values[i]) + data.unit;
      svg.appendChild(dot);
      var lab = el("text", { class: "tick tick--x", x: p[0], y: H - 12 });
      lab.textContent = data.labels[i];
      svg.appendChild(lab);
    });
    svg.appendChild(el("line", { class: "axis", x1: padL, x2: W - padR, y1: padT + ih, y2: padT + ih }));
    return svg;
  }

  function fmt(v) {
    if (v === 0) return "0";
    return Math.abs(v) >= 10 ? String(Math.round(v)) : String(Math.round(v * 10) / 10);
  }

  function initCharts() {
    var charts = doc.querySelectorAll("[data-cmp-chart]");
    Array.prototype.forEach.call(charts, function (chart) {
      var data = readData(chart);
      var plot = chart.querySelector(".cmp-chart__plot");
      if (!data || !plot || !data.values.length) return;
      var svg = chart.getAttribute("data-chart") === "line" ? drawLine(chart, data) : drawBar(chart, data);
      plot.appendChild(svg);

      var toggle = chart.querySelector("[data-cmp-chart-toggle]");
      var table = chart.querySelector(".cmp-chart__data");
      if (toggle && table) {
        toggle.addEventListener("click", function () {
          var open = table.hasAttribute("hidden");
          if (open) { table.removeAttribute("hidden"); toggle.textContent = toggle.getAttribute("data-label-hide") || "Hide the numbers"; }
          else { table.setAttribute("hidden", ""); toggle.textContent = toggle.getAttribute("data-label-show") || "Show the numbers"; }
        });
      }
    });
  }

  /* ------------------------------------------------------------------ init */
  function init() {
    initTables();
    initDetails();
    initVideo();
    initGallery();
    initTabs();
    initCharts();
  }

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
