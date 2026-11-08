"""Generate ``legacy_0_6_1.json``, the reference outputs of python-aqi 0.6.1.

Run it with the 0.6.1 sources first on the path, from a checkout of that tag::

    git worktree add /tmp/aqi061 0.6.1
    cd /tmp/aqi061 && python /path/to/tests/data/generate_legacy.py > legacy_0_6_1.json

Only inputs that 0.6.1 answered are recorded, the rest (gaps, out of range
values, the broken first EPA 1h ozone bands) is not part of the contract.
"""

import json
import sys

import aqi
import aqi.algos.epa
import aqi.algos.mep

out = {}
for name, mod in (("epa", aqi.algos.epa), ("mep", aqi.algos.mep)):
    algo = mod.AQI()
    pw = algo.piecewise
    entry = {"iaqi": {}, "cc": {}}
    for elem, bps in pw["bp"].items():
        prec = pw["prec"][elem]
        top = bps[-1][1]
        ccs = set()
        for lo, hi in bps:
            span = int((hi - lo) / prec)
            stride = max(1, span // 40)
            for k in range(0, span + 1, stride):
                ccs.add(lo + prec * k)
            ccs.update({lo, hi, lo + prec, hi - prec})
        iaqis = {}
        for value in sorted(c for c in ccs if 0 <= c <= top):
            try:
                iaqis[str(value)] = int(algo.iaqi(elem, str(value)))
            except Exception:
                pass
        entry["iaqi"][elem] = iaqis
        cc = {}
        for i in range(0, 501):
            try:
                cc[str(i)] = str(algo.cc(elem, str(i)))
            except Exception:
                pass
        entry["cc"][elem] = cc
    out[name] = entry
json.dump(out, sys.stdout, separators=(",", ":"), sort_keys=True)
