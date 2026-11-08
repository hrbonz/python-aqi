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


class MEP_2012(PiecewiseAQI):
    """Implementation of the MEP AQI algorithm, HJ 633-2012, as python-aqi has
    always computed it.

    It is the tables of the standard laid out like the EPA ones (a gap between
    two bands, concentrations truncated to integers, IAQI rounded half to
    even), which is not what HJ 633-2012 says: its formula interpolates between
    the limits of table 1, IAQI and AQI are rounded up (clause 6.2) and CO has
    one decimal (issue 4). :class:`MEP_2026` follows its standard, this class
    is kept for compatibility.

    Source: HJ 633-2012 (``docs/standards``).
    """

    piecewise = {
        "aqi": [
            (0, 50),
            (51, 100),
            (101, 150),
            (151, 200),
            (201, 300),
            (301, 400),
            (401, 500),
        ],
        "bp": {
            POLLUTANT_SO2_24H: [
                (Decimal("0.0"), Decimal("50")),
                (Decimal("51"), Decimal("150")),
                (Decimal("151"), Decimal("475")),
                (Decimal("476"), Decimal("800")),
                (Decimal("801"), Decimal("1600")),
                (Decimal("1601"), Decimal("2100")),
                (Decimal("2101"), Decimal("2620")),
            ],
            POLLUTANT_SO2_1H: [
                (Decimal("0.0"), Decimal("150")),
                (Decimal("151"), Decimal("500")),
                (Decimal("501"), Decimal("650")),
                (Decimal("651"), Decimal("800")),
            ],
            POLLUTANT_NO2_24H: [
                (Decimal("0.0"), Decimal("40")),
                (Decimal("41"), Decimal("80")),
                (Decimal("81"), Decimal("180")),
                (Decimal("181"), Decimal("280")),
                (Decimal("281"), Decimal("565")),
                (Decimal("566"), Decimal("750")),
                (Decimal("751"), Decimal("940")),
            ],
            POLLUTANT_NO2_1H: [
                (Decimal("0.0"), Decimal("100")),
                (Decimal("101"), Decimal("200")),
                (Decimal("201"), Decimal("700")),
                (Decimal("701"), Decimal("1200")),
                (Decimal("1201"), Decimal("2340")),
                (Decimal("2341"), Decimal("3090")),
                (Decimal("3091"), Decimal("3840")),
            ],
            POLLUTANT_PM10: [
                (Decimal("00"), Decimal("50")),
                (Decimal("51"), Decimal("150")),
                (Decimal("151"), Decimal("250")),
                (Decimal("251"), Decimal("350")),
                (Decimal("351"), Decimal("420")),
                (Decimal("421"), Decimal("500")),
                (Decimal("501"), Decimal("600")),
            ],
            POLLUTANT_CO_24H: [
                (Decimal("0.0"), Decimal("2")),
                (Decimal("3"), Decimal("4")),
                (Decimal("5"), Decimal("14")),
                (Decimal("15"), Decimal("24")),
                (Decimal("25"), Decimal("36")),
                (Decimal("37"), Decimal("48")),
                (Decimal("49"), Decimal("60")),
            ],
            POLLUTANT_CO_1H: [
                (Decimal("0.0"), Decimal("5")),
                (Decimal("6"), Decimal("10")),
                (Decimal("11"), Decimal("35")),
                (Decimal("36"), Decimal("60")),
                (Decimal("61"), Decimal("90")),
                (Decimal("91"), Decimal("120")),
                (Decimal("121"), Decimal("150")),
            ],
            POLLUTANT_O3_1H: [
                (Decimal("0.0"), Decimal("160")),
                (Decimal("161"), Decimal("200")),
                (Decimal("201"), Decimal("300")),
                (Decimal("301"), Decimal("400")),
                (Decimal("401"), Decimal("800")),
                (Decimal("801"), Decimal("1000")),
                (Decimal("1001"), Decimal("1200")),
            ],
            POLLUTANT_O3_8H: [
                (Decimal("0.0"), Decimal("100")),
                (Decimal("101"), Decimal("160")),
                (Decimal("161"), Decimal("215")),
                (Decimal("216"), Decimal("265")),
                (Decimal("266"), Decimal("800")),
            ],
            POLLUTANT_PM25: [
                (Decimal("0.0"), Decimal("35")),
                (Decimal("36"), Decimal("75")),
                (Decimal("76"), Decimal("115")),
                (Decimal("116"), Decimal("150")),
                (Decimal("151"), Decimal("250")),
                (Decimal("251"), Decimal("350")),
                (Decimal("351"), Decimal("500")),
            ],
        },
        "prec": {
            POLLUTANT_O3_8H: Decimal("1."),
            POLLUTANT_O3_1H: Decimal("1."),
            POLLUTANT_PM10: Decimal("1."),
            POLLUTANT_PM25: Decimal("1."),
            POLLUTANT_CO_1H: Decimal("1."),
            POLLUTANT_CO_24H: Decimal("1."),
            POLLUTANT_SO2_1H: Decimal("1."),
            POLLUTANT_SO2_24H: Decimal("1."),
            POLLUTANT_NO2_1H: Decimal("1."),
            POLLUTANT_NO2_24H: Decimal("1."),
        },
        "units": {
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
        },
    }


# HJ 633-2026 table 3: the concentration limit of each IAQI, 0 to 500 (the IAQI
# are 0, 50, 100, 150, 200, 300, 400 and 500), blank cells are left out
_LIMITS_2026 = {
    POLLUTANT_SO2_24H: "0 50 150 475 800 1600 2100 2620",
    POLLUTANT_SO2_1H: "0 150 500 650 800",
    POLLUTANT_NO2_24H: "0 40 80 180 280 565 750 940",
    POLLUTANT_NO2_1H: "0 100 200 700 1200 2340 3090 3840",
    POLLUTANT_CO_24H: "0 2 4 14 24 36 48 60",
    POLLUTANT_CO_1H: "0 5 10 35 60 90 120 150",
    POLLUTANT_O3_8H: "0 100 160 215 265 800",
    POLLUTANT_O3_1H: "0 160 200 300 400 800 1000 1200",
    POLLUTANT_PM10: "0 50 120 250 350 420 500 600",
    POLLUTANT_PM25: "0 35 60 115 150 250 350 500",
}


def _bands(limits):
    """Each band goes from a limit to the next one: the formula (1) of the
    standard interpolates between neighbouring limits of the table"""
    points = [Decimal(limit) for limit in limits.split()]
    return list(zip(points, points[1:]))


class MEP_2026(MEP_2012):
    """MEP AQI algorithm, HJ 633-2026 (replaces HJ 633-2012, effective
    1 March 2026).

    Compared with HJ 633-2012 the limits of IAQI 100 change for PM10 (150 to
    120 µg/m³) and PM2.5 (75 to 60 µg/m³). The calculation follows the
    standard: the formula interpolates between neighbouring limits of table 3
    (clause 4.2.4), concentrations are rounded to integers and CO to one
    decimal following GB/T 8170, half to even (clause 4.2.2), and IAQI and AQI
    are rounded up (clause 4.2.6). Above the table, SO2 1 hour is IAQI 200
    and O3 8 hour is IAQI 300 (notes b and c), any other value is out of range.

    Source: HJ 633-2026, table 3 and clauses 4.2.2 to 4.2.6
    (``docs/standards``, transcription in ``hj633-2026-table.rst``).
    """

    rounding = ROUND_CEILING
    cc_rounding = ROUND_HALF_EVEN
    saturation = {POLLUTANT_SO2_1H: 200, POLLUTANT_O3_8H: 300}

    piecewise = derive_piecewise(
        MEP_2012.piecewise,
        aqi=[(0, 50), (50, 100), (100, 150), (150, 200), (200, 300), (300, 400)]
        + [(400, 500)],
        bp={elem: _bands(limits) for elem, limits in _LIMITS_2026.items()},
        prec={POLLUTANT_CO_24H: Decimal("0.1"), POLLUTANT_CO_1H: Decimal("0.1")},
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
