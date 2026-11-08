from decimal import ROUND_CEILING, ROUND_HALF_EVEN, Decimal

from aqi.algos.base import PiecewiseAQI, derive_piecewise
from aqi.constants import (
    POLLUTANT_CO_1H,
    POLLUTANT_CO_24H,
    POLLUTANT_NO2_1H,
    POLLUTANT_NO2_24H,
    POLLUTANT_O3_1H,
    POLLUTANT_O3_8H,
    POLLUTANT_PM10,
    POLLUTANT_PM25,
    POLLUTANT_SO2_1H,
    POLLUTANT_SO2_24H,
)

# HJ 633-2012 table 1: the concentration limit of each IAQI, 0 to 500 (the IAQI
# are 0, 50, 100, 150, 200, 300, 400 and 500), blank cells are left out
_LIMITS_2012 = {
    POLLUTANT_SO2_24H: "0 50 150 475 800 1600 2100 2620",
    POLLUTANT_SO2_1H: "0 150 500 650 800",
    POLLUTANT_NO2_24H: "0 40 80 180 280 565 750 940",
    POLLUTANT_NO2_1H: "0 100 200 700 1200 2340 3090 3840",
    POLLUTANT_CO_24H: "0 2 4 14 24 36 48 60",
    POLLUTANT_CO_1H: "0 5 10 35 60 90 120 150",
    POLLUTANT_O3_8H: "0 100 160 215 265 800",
    POLLUTANT_O3_1H: "0 160 200 300 400 800 1000 1200",
    POLLUTANT_PM10: "0 50 150 250 350 420 500 600",
    POLLUTANT_PM25: "0 35 75 115 150 250 350 500",
}

_UNITS = {
    POLLUTANT_SO2_24H: "µg/m³",
    POLLUTANT_SO2_1H: "µg/m³",
    POLLUTANT_NO2_24H: "µg/m³",
    POLLUTANT_NO2_1H: "µg/m³",
    POLLUTANT_PM10: "µg/m³",
    POLLUTANT_CO_24H: "mg/m³",
    POLLUTANT_CO_1H: "mg/m³",
    POLLUTANT_O3_1H: "µg/m³",
    POLLUTANT_O3_8H: "µg/m³",
    POLLUTANT_PM25: "µg/m³",
}


def _bands(limits):
    """Each band goes from a limit to the next one: the formula (1) of the
    standards interpolates between neighbouring limits of the table"""
    points = [Decimal(limit) for limit in limits.split()]
    return list(zip(points, points[1:]))


class MEP_2012(PiecewiseAQI):
    """MEP AQI algorithm, HJ 633-2012 (in force from 1 January 2016, replaced
    by HJ 633-2026 on 1 March 2026).

    The calculation follows the standard: the formula (1) interpolates between
    neighbouring limits of table 1, concentrations are used as they are given
    (the standard does not round them) and IAQI and AQI are rounded up
    (clause 6.2). SO2 1 hour and O3 8 hour above 800 µg/m³ are not computed
    (notes 2 and 3 of table 1): :class:`NotApplicableError`, and :meth:`aqi`
    leaves them out, the 24 hour SO2 and the 1 hour O3 are used instead.

    Before 1.0 this class was laid out like the EPA tables (gaps between bands,
    concentrations truncated to integers, IAQI rounded half to even), so some
    results differ from python-aqi 0.6, see the changelog.

    Source: HJ 633-2012, table 1 and clauses 4.2 and 6.2 (``docs/standards``).
    """

    rounding = ROUND_CEILING
    undefined_above = (POLLUTANT_SO2_1H, POLLUTANT_O3_8H)

    piecewise = {
        "aqi": [(0, 50), (50, 100), (100, 150), (150, 200), (200, 300), (300, 400)]
        + [(400, 500)],
        "bp": {elem: _bands(limits) for elem, limits in _LIMITS_2012.items()},
        "prec": dict.fromkeys(_LIMITS_2012),
        "units": _UNITS,
    }


class MEP_2026(MEP_2012):
    """MEP AQI algorithm, HJ 633-2026 (replaces HJ 633-2012, effective
    1 March 2026).

    Compared with HJ 633-2012 the limits of IAQI 100 change for PM10 (150 to
    120 µg/m³) and PM2.5 (75 to 60 µg/m³). The calculation is the same except
    that concentrations are rounded to integers and CO to one decimal
    following GB/T 8170, half to even (clause 4.2.2), and that above the table
    SO2 1 hour is IAQI 200 and O3 8 hour is IAQI 300 (notes b and c), any other
    value is out of range.

    Source: HJ 633-2026, table 3 and clauses 4.2.2 to 4.2.6
    (``docs/standards``, transcription in ``hj633-2026-table.rst``).
    """

    cc_rounding = ROUND_HALF_EVEN
    saturation = {POLLUTANT_SO2_1H: 200, POLLUTANT_O3_8H: 300}
    undefined_above = ()

    piecewise = derive_piecewise(
        MEP_2012.piecewise,
        bp={
            elem: _bands(limits)
            for elem, limits in {
                POLLUTANT_PM10: "0 50 120 250 350 420 500 600",
                POLLUTANT_PM25: "0 35 60 115 150 250 350 500",
            }.items()
        },
        prec={
            **dict.fromkeys(_LIMITS_2012, Decimal("1.")),
            POLLUTANT_CO_24H: Decimal("0.1"),
            POLLUTANT_CO_1H: Decimal("0.1"),
        },
    )


# oldest first, the last one is the latest and the default
VERSIONS = {
    "2012": MEP_2012,
    "2026": MEP_2026,
}

#: the latest version of the MEP algorithm
MEP = list(VERSIONS.values())[-1]
#: historical name, the module is loaded by ``aqi.algos.get_algo``
AQI = MEP
