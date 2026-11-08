"""Data for the comparison charts of the standards versions.

The curves are computed with the library (``iaqi`` at the edge of every band),
so the charts cannot drift from the code. The label and the effective date of
a version are facts of the standards, they are listed here and a test checks
that no version of the library is missing.
"""

import json
from decimal import Decimal
from html import escape

from docutils import nodes
from docutils.parsers.rst import Directive

from aqi.algos import FAMILIES, available_algos, get_algo

FAMILY_LABELS = {
    "epa": "EPA (United States)",
    "mep": "MEP (China)",
}

# the standard behind each version and the date it came into force
VERSIONS = {
    "epa:2012": {"standard": "PM2.5 NAAQS 2012, 78 FR 3086", "effective": "2013-03-18"},
    "epa:2015": {
        "standard": "Ozone NAAQS 2015, 80 FR 65292",
        "effective": "2015-12-28",
    },
    "epa:2024": {
        "standard": "PM2.5 NAAQS 2024, 89 FR 16202",
        "effective": "2024-05-06",
    },
    "mep:2012": {"standard": "HJ 633-2012", "effective": "2016-01-01"},
    "mep:2026": {"standard": "HJ 633-2026", "effective": "2026-03-01"},
}


def _number(value):
    """A JSON number without trailing zeros (0.0 -> 0, 12.10 -> 12.1)"""
    value = Decimal(value).normalize()
    return int(value) if value == value.to_integral() else float(value)


def pollutant_curve(algo, elem):
    """Return ``(curve, bands)`` of a pollutant.

    ``curve`` is the list of ``[concentration, IAQI]`` at the edges of the
    bands, joined by straight lines it is the conversion function. ``bands`` is
    the list of ``[IAQI low, IAQI high, concentration low, concentration high]``
    of the bands the standard defines (blank bands are left out).
    """
    pw = algo.piecewise
    curve, bands = [], []
    for (ilo, ihi), bp in zip(pw["aqi"], pw["bp"][elem]):
        if bp is None or bp == (0, 0):
            continue
        lo, hi = (Decimal(v) for v in bp)
        bands.append([ilo, ihi, _number(lo), _number(hi)])
        for edge in (lo, hi):
            point = [_number(edge), _number(algo.iaqi(elem, str(edge)))]
            if point not in curve:
                curve.append(point)
    return curve, bands


def build_data(family):
    """Everything the page of a family needs, ready for ``json.dumps``"""
    versions = [name for name in available_algos() if name.startswith(family + ":")]
    data = {
        "family": family,
        "label": FAMILY_LABELS[family],
        "versions": [],
        "pollutants": {},
    }
    for name in versions:
        algo = get_algo(name)
        data["versions"].append({"id": name, **VERSIONS[name]})
        for elem in sorted(algo.piecewise["bp"]):
            entry = data["pollutants"].setdefault(
                elem, {"unit": algo.piecewise["units"][elem], "versions": {}}
            )
            curve, bands = pollutant_curve(algo, elem)
            entry["versions"][name] = {"curve": curve, "bands": bands}
    return data


def families():
    return list(FAMILIES)


def static_tables(data, algos):
    """Return ``{elem: [(band label, {version: range text})]}``.

    One row per band of the AQI scale, one column per version, the text is
    the range of concentrations. Bands that a version does not have are blank.
    """
    tables = {}
    for elem, entry in data["pollutants"].items():
        rows = {}
        for name, info in entry["versions"].items():
            exp = Decimal(algos[name].piecewise["prec"][elem])
            for ilo, ihi, lo, hi in info["bands"]:
                lo, hi = (Decimal(str(v)).quantize(exp) for v in (lo, hi))
                rows.setdefault((ilo, ihi), {})[name] = f"{lo}\u00a0–\u00a0{hi}"
        tables[elem] = [
            (f"{ilo}\u00a0–\u00a0{ihi}", cells)
            for (ilo, ihi), cells in sorted(rows.items())
        ]
    return tables


def render_html(family):
    """The HTML of a family block: the data, and the tables used without JS"""
    data = build_data(family)
    algos = {v["id"]: get_algo(v["id"]) for v in data["versions"]}
    tables = static_tables(data, algos)
    out = [f'<div class="aqi-compare" data-family="{family}">']
    # "</" can not end the script element early
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    out.append(f'<script type="application/json" class="aqi-data">{payload}</script>')
    out.append('<div class="aqi-controls"></div><div class="aqi-chart"></div>')
    for elem, rows in tables.items():
        unit = escape(data["pollutants"][elem]["unit"])
        out.append(f'<div class="aqi-pollutant" data-elem="{escape(elem)}">')
        out.append(f"<h4>{escape(elem)} ({unit})</h4>")
        out.append('<table class="aqi-breakpoints"><thead><tr><th>AQI</th>')
        for version in data["versions"]:
            out.append(f'<th data-version="{version["id"]}">{version["id"]}</th>')
        out.append("</tr></thead><tbody>")
        for label, cells in rows:
            out.append(f"<tr><th>{label}</th>")
            for version in data["versions"]:
                text = cells.get(version["id"], "–")
                out.append(f'<td data-version="{version["id"]}">{text}</td>')
            out.append("</tr>")
        out.append("</tbody></table></div>")
    out.append("</div>")
    return "".join(out)


class CompareDirective(Directive):
    """``.. aqi-compare:: epa``: charts and tables of the versions of a family"""

    required_arguments = 1

    def run(self):
        family = self.arguments[0]
        if family not in FAMILIES:
            raise self.error(f"unknown algorithm family {family!r}")
        env = self.state.document.settings.env
        env.metadata[env.docname]["aqi-compare"] = "1"
        return [nodes.raw("", render_html(family), format="html")]


ASSETS = ("uPlot.min.css", "aqi_compare.css")
SCRIPTS = ("uPlot.iife.min.js", "aqi_compare.js")


def add_assets(app, pagename, templatename, context, doctree):
    """Load the chart files on the pages that have a comparison only"""
    if "aqi-compare" not in app.env.metadata.get(pagename, {}):
        return
    pathto = context["pathto"]
    tags = [
        f'<link rel="stylesheet" href="{pathto("_static/" + name, 1)}">'
        for name in ASSETS
    ] + [
        f'<script defer src="{pathto("_static/" + name, 1)}"></script>'
        for name in SCRIPTS
    ]
    # themes differ on what they do with the head, the body is always used
    context["body"] = context["body"] + "\n".join(tags)


def setup(app):
    app.add_directive("aqi-compare", CompareDirective)
    app.connect("html-page-context", add_assets)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
