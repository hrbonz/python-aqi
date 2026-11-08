/* Interactive comparison of the versions of an AQI standard (uPlot).
 * The data is inline in the page, the tables are the content without JS. */
(function () {
  "use strict";
  var COLORS = ["#0f766e", "#d97706", "#7c3aed", "#dc2626", "#2563eb"];

  function isDark() {
    var root = document.documentElement;
    var theme = root.getAttribute("data-theme");
    if (theme) return theme === "dark";
    if (root.classList.contains("dark")) return true;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { node.setAttribute(k, attrs[k]); });
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function init(root) {
    var script = root.querySelector("script.aqi-data");
    if (!script || !window.uPlot) return;
    var data = JSON.parse(script.textContent);
    var elems = Object.keys(data.pollutants);
    var state = { elem: elems.indexOf("pm25") >= 0 ? "pm25" : elems[0],
                  versions: data.versions.map(function (v) { return v.id; }) };
    var colorOf = {};
    data.versions.forEach(function (v, i) { colorOf[v.id] = COLORS[i % COLORS.length]; });
    var controls = root.querySelector(".aqi-controls");
    var holder = root.querySelector(".aqi-chart");
    var plot = null;

    root.classList.add("aqi-js");
    root.querySelectorAll("table").forEach(function (t) {
      var wrap = el("div", { "class": "aqi-table-wrap" });
      t.parentNode.insertBefore(wrap, t);
      wrap.appendChild(t);
    });

    var field = el("fieldset");
    field.appendChild(el("legend", {}, "Pollutant"));
    var select = el("select", { "aria-label": "Pollutant" });
    elems.forEach(function (e) {
      var opt = el("option", { value: e }, e + " (" + data.pollutants[e].unit + ")");
      if (e === state.elem) opt.selected = true;
      select.appendChild(opt);
    });
    select.addEventListener("change", function () { state.elem = select.value; draw(); });
    field.appendChild(select);
    controls.appendChild(field);

    var vfield = el("fieldset");
    vfield.appendChild(el("legend", {}, "Versions"));
    data.versions.forEach(function (v) {
      var label = el("label");
      var box = el("input", { type: "checkbox", value: v.id });
      box.checked = true;
      box.addEventListener("change", function () {
        state.versions = Array.prototype.filter.call(
          vfield.querySelectorAll("input"), function (b) { return b.checked; }
        ).map(function (b) { return b.value; });
        draw();
      });
      var dot = el("span", { "class": "aqi-swatch" });
      dot.style.background = colorOf[v.id];
      label.appendChild(box);
      label.appendChild(document.createTextNode(" "));
      label.appendChild(dot);
      label.appendChild(document.createTextNode(v.id + " "));
      label.appendChild(el("small", {}, v.standard + ", effective " + v.effective));
      vfield.appendChild(label);
    });
    controls.appendChild(vfield);

    function series() {
      var entry = data.pollutants[state.elem];
      var names = state.versions.filter(function (n) { return entry.versions[n]; });
      var xs = [];
      names.forEach(function (n) {
        entry.versions[n].curve.forEach(function (p) { if (xs.indexOf(p[0]) < 0) xs.push(p[0]); });
      });
      xs.sort(function (a, b) { return a - b; });
      var cols = names.map(function (n) {
        var map = {};
        entry.versions[n].curve.forEach(function (p) { map[p[0]] = p[1]; });
        return xs.map(function (x) { return map.hasOwnProperty(x) ? map[x] : null; });
      });
      return { names: names, aligned: [xs].concat(cols), unit: entry.unit };
    }

    function tables() {
      root.querySelectorAll(".aqi-pollutant").forEach(function (div) {
        div.style.display = div.getAttribute("data-elem") === state.elem ? "" : "none";
      });
      var div = root.querySelector('.aqi-pollutant[data-elem="' + state.elem + '"]');
      if (!div) return;
      div.querySelectorAll("[data-version]").forEach(function (cell) {
        cell.style.display = state.versions.indexOf(cell.getAttribute("data-version")) < 0 ? "none" : "";
        cell.classList.remove("aqi-diff");
      });
      /* highlight what changed since the previous selected version */
      div.querySelectorAll("tbody tr").forEach(function (row) {
        var prev = null;
        state.versions.forEach(function (v) {
          var cell = row.querySelector('td[data-version="' + v + '"]');
          if (!cell) return;
          if (prev !== null && cell.textContent !== prev) cell.classList.add("aqi-diff");
          prev = cell.textContent;
        });
      });
    }

    function draw() {
      tables();
      if (plot) { plot.destroy(); plot = null; }
      holder.textContent = "";
      var s = series();
      if (!s.names.length) { holder.textContent = "Select at least one version."; return; }
      var dark = isDark();
      var fg = dark ? "#cbd5e1" : "#334155";
      var grid = dark ? "rgba(203,213,225,.15)" : "rgba(51,65,85,.12)";
      var opts = {
        width: holder.clientWidth || 600,
        height: Math.max(300, Math.min(420, Math.round((holder.clientWidth || 600) * 0.6))),
        scales: { x: { time: false } },
        axes: [
          { label: "Concentration (" + s.unit + ")", stroke: fg, grid: { stroke: grid }, ticks: { stroke: grid } },
          { label: "IAQI", stroke: fg, grid: { stroke: grid }, ticks: { stroke: grid }, size: 60 }
        ],
        series: [{ label: "concentration" }].concat(s.names.map(function (n) {
          return { label: n, stroke: colorOf[n], width: 2, spanGaps: true,
                   points: { show: true, size: 5, fill: colorOf[n] } };
        })),
        legend: { live: true }
      };
      plot = new uPlot(opts, s.aligned, holder);
    }

    var timer = null;
    window.addEventListener("resize", function () {
      clearTimeout(timer);
      timer = setTimeout(function () { if (plot) draw(); }, 150);
    });
    /* follow the colour scheme of the theme */
    new MutationObserver(function () { draw(); }).observe(
      document.documentElement, { attributes: true, attributeFilter: ["data-theme", "class"] });
    if (window.matchMedia) {
      var mq = window.matchMedia("(prefers-color-scheme: dark)");
      (mq.addEventListener ? mq.addEventListener.bind(mq, "change") : mq.addListener.bind(mq))(draw);
    }
    draw();
  }

  function start() { document.querySelectorAll(".aqi-compare").forEach(init); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
