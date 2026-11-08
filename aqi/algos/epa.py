from decimal import Decimal

from aqi.algos.base import PiecewiseAQI, derive_piecewise
from aqi.constants import (
    POLLUTANT_CO_8H,
    POLLUTANT_NO2_1H,
    POLLUTANT_O3_1H,
    POLLUTANT_O3_8H,
    POLLUTANT_PM10,
    POLLUTANT_PM25,
    POLLUTANT_SO2_1H,
)


class EPA_2012(PiecewiseAQI):
    """Implementation of the EPA AQI algorithm, as python-aqi has always
    computed it: the PM2.5 breakpoints of the 2012 revision (annual standard
    lowered to 12 µg/m³) and the 1997 ozone 8 hour breakpoints.

    Source: Technical Assistance Document EPA-454/B-13-001, December 2013, and
    the Federal Register of 15 January 2013 (78 FR 3286), both in
    ``docs/standards``. The ``(0, 0)`` first bands of 1 hour ozone are a known
    flaw (issue 15) that is kept here, later versions leave them blank.

    Above 500 the EPA calls values "Beyond the AQI" and computes them with
    the Hazardous breakpoints (Technical Assistance Document, Q&A), this is
    available with ``extrapolate=True``.
    """

    extrapolation = True

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
            POLLUTANT_O3_8H: [
                (Decimal("0.000"), Decimal("0.059")),
                (Decimal("0.060"), Decimal("0.075")),
                (Decimal("0.076"), Decimal("0.095")),
                (Decimal("0.096"), Decimal("0.115")),
                (Decimal("0.116"), Decimal("0.374")),
            ],
            POLLUTANT_O3_1H: [
                (0, 0),
                (0, 0),
                (Decimal("0.125"), Decimal("0.164")),
                (Decimal("0.165"), Decimal("0.204")),
                (Decimal("0.205"), Decimal("0.404")),
                (Decimal("0.405"), Decimal("0.504")),
                (Decimal("0.505"), Decimal("0.604")),
            ],
            POLLUTANT_PM10: [
                (Decimal("0"), Decimal("54")),
                (Decimal("55"), Decimal("154")),
                (Decimal("155"), Decimal("254")),
                (Decimal("255"), Decimal("354")),
                (Decimal("355"), Decimal("424")),
                (Decimal("425"), Decimal("504")),
                (Decimal("505"), Decimal("604")),
            ],
            POLLUTANT_PM25: [
                (Decimal("0.0"), Decimal("12.0")),
                (Decimal("12.1"), Decimal("35.4")),
                (Decimal("35.5"), Decimal("55.4")),
                (Decimal("55.5"), Decimal("150.4")),
                (Decimal("150.5"), Decimal("250.4")),
                (Decimal("250.5"), Decimal("350.4")),
                (Decimal("350.5"), Decimal("500.4")),
            ],
            POLLUTANT_CO_8H: [
                (Decimal("0.0"), Decimal("4.4")),
                (Decimal("4.5"), Decimal("9.4")),
                (Decimal("9.5"), Decimal("12.4")),
                (Decimal("12.5"), Decimal("15.4")),
                (Decimal("15.5"), Decimal("30.4")),
                (Decimal("30.5"), Decimal("40.4")),
                (Decimal("40.5"), Decimal("50.4")),
            ],
            POLLUTANT_SO2_1H: [
                (Decimal("0"), Decimal("35")),
                (Decimal("36"), Decimal("75")),
                (Decimal("76"), Decimal("185")),
                (Decimal("186"), Decimal("304")),
                (Decimal("305"), Decimal("604")),
                (Decimal("605"), Decimal("804")),
                (Decimal("805"), Decimal("1004")),
            ],
            POLLUTANT_NO2_1H: [
                (Decimal("0"), Decimal("53")),
                (Decimal("54"), Decimal("100")),
                (Decimal("101"), Decimal("360")),
                (Decimal("361"), Decimal("649")),
                (Decimal("650"), Decimal("1249")),
                (Decimal("1250"), Decimal("1649")),
                (Decimal("1650"), Decimal("2049")),
            ],
        },
        "prec": {
            POLLUTANT_O3_8H: Decimal(".001"),
            POLLUTANT_O3_1H: Decimal(".001"),
            POLLUTANT_PM10: Decimal("1."),
            POLLUTANT_PM25: Decimal(".1"),
            POLLUTANT_CO_8H: Decimal(".1"),
            POLLUTANT_SO2_1H: Decimal("1."),
            POLLUTANT_NO2_1H: Decimal("1."),
        },
        "units": {
            POLLUTANT_O3_8H: "ppm",
            POLLUTANT_O3_1H: "ppm",
            POLLUTANT_PM10: "µg/m³",
            POLLUTANT_PM25: "µg/m³",
            POLLUTANT_CO_8H: "ppm",
            POLLUTANT_SO2_1H: "ppb",
            POLLUTANT_NO2_1H: "ppb",
        },
    }


class EPA_2015(EPA_2012):
    """EPA AQI after the 2015 ozone standard (0.070 ppm): new 8 hour ozone
    breakpoints, 1 hour ozone starts at 0.125 ppm (AQI 101) and the lower
    bands are blank, as in the table of the standard.

    Source: Technical Assistance Document EPA-454/B-18-007, September 2018,
    Table 5 (``docs/standards``).
    """

    piecewise = derive_piecewise(
        EPA_2012.piecewise,
        bp={
            POLLUTANT_O3_8H: [
                (Decimal("0.000"), Decimal("0.054")),
                (Decimal("0.055"), Decimal("0.070")),
                (Decimal("0.071"), Decimal("0.085")),
                (Decimal("0.086"), Decimal("0.105")),
                (Decimal("0.106"), Decimal("0.200")),
            ],
            POLLUTANT_O3_1H: [
                None,
                None,
                (Decimal("0.125"), Decimal("0.164")),
                (Decimal("0.165"), Decimal("0.204")),
                (Decimal("0.205"), Decimal("0.404")),
                (Decimal("0.405"), Decimal("0.504")),
                (Decimal("0.505"), Decimal("0.604")),
            ],
        },
    )


class EPA_2024(EPA_2015):
    """EPA AQI after the 2024 PM2.5 standard (annual 9 µg/m³), effective
    6 May 2024: new PM2.5 breakpoints, and a single Hazardous category,
    AQI 301 to 500, for every pollutant. Its top is the concentration of
    AQI 500, so PM10, CO, SO2, NO2 and 1 hour ozone above their old 400 are
    now on one linear band instead of two (PM10 504 µg/m³ is 389, not 400).

    Source: Technical Assistance Document EPA-403/B-26-003, May 2026, Table 6
    (same table as EPA-454/B-24-002, May 2024), in ``docs/standards``.
    """

    _hazardous = {
        POLLUTANT_O3_1H: (Decimal("0.405"), Decimal("0.604")),
        POLLUTANT_PM10: (Decimal("425"), Decimal("604")),
        POLLUTANT_CO_8H: (Decimal("30.5"), Decimal("50.4")),
        POLLUTANT_SO2_1H: (Decimal("605"), Decimal("1004")),
        POLLUTANT_NO2_1H: (Decimal("1250"), Decimal("2049")),
    }

    piecewise = derive_piecewise(
        EPA_2015.piecewise,
        aqi=[(0, 50), (51, 100), (101, 150), (151, 200), (201, 300), (301, 500)],
        bp={
            POLLUTANT_PM25: [
                (Decimal("0.0"), Decimal("9.0")),
                (Decimal("9.1"), Decimal("35.4")),
                (Decimal("35.5"), Decimal("55.4")),
                (Decimal("55.5"), Decimal("125.4")),
                (Decimal("125.5"), Decimal("225.4")),
                (Decimal("225.5"), Decimal("325.4")),
            ],
            **{
                elem: [*EPA_2015.piecewise["bp"][elem][:5], hazardous]
                for elem, hazardous in _hazardous.items()
            },
        },
    )


# oldest first, the last one is the latest and the default
VERSIONS = {
    "2012": EPA_2012,
    "2015": EPA_2015,
    "2024": EPA_2024,
}

#: the latest version of the EPA algorithm
EPA = list(VERSIONS.values())[-1]
#: historical name, the module is loaded by ``aqi.algos.get_algo``
AQI = EPA
