"""Sphinx directive printing the breakpoint table of an algorithm version.

    .. aqi-breakpoints:: epa:2024

The table is built from the library, so the documentation cannot drift from the
code. Each column is a band of the AQI scale, each row a pollutant, a cell is
the range of concentrations of the band.
"""

from decimal import Decimal

from docutils import nodes
from docutils.parsers.rst import Directive

from aqi.algos import get_algo

# a range stays on one line, only the columns wrap
RANGE = "{lo}\u00a0–\u00a0{hi}"


def _cell(*children):
    entry = nodes.entry()
    for child in children:
        entry += nodes.paragraph(text=child) if isinstance(child, str) else child
    return entry


def _row(*cells):
    row = nodes.row()
    for cell in cells:
        row += cell
    return row


def build_rows(name):
    """Return ``(header, rows)`` as lists of strings for an algorithm name"""
    algo = get_algo(name)
    if algo is None:
        raise ValueError(f"unknown algorithm {name!r}")
    pw = algo.piecewise
    header = ["Pollutant (unit)"] + [RANGE.format(lo=lo, hi=hi) for lo, hi in pw["aqi"]]
    rows = []
    for elem in sorted(pw["bp"]):
        exp = Decimal(pw["prec"][elem])
        cells = []
        for bp in pw["bp"][elem]:
            if bp is None or bp == (0, 0):
                cells.append("–")
            else:
                lo, hi = (Decimal(v).quantize(exp) for v in bp)
                cells.append(RANGE.format(lo=lo, hi=hi))
        cells += ["–"] * (len(pw["aqi"]) - len(cells))
        rows.append([f"{elem} ({pw['units'][elem]})"] + cells)
    return header, rows


class BreakpointsDirective(Directive):
    required_arguments = 1

    def run(self):
        header, rows = build_rows(self.arguments[0])
        table = nodes.table(classes=["aqi-breakpoints"])
        tgroup = nodes.tgroup(cols=len(header))
        table += tgroup
        for _ in header:
            tgroup += nodes.colspec(colwidth=1)
        thead = nodes.thead()
        thead += _row(*(_cell(text) for text in header))
        tgroup += thead
        tbody = nodes.tbody()
        for row in rows:
            tbody += _row(*(_cell(text) for text in row))
        tgroup += tbody
        return [table]


def setup(app):
    app.add_directive("aqi-breakpoints", BreakpointsDirective)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
