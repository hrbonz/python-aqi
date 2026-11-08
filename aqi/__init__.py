from aqi.algos import available_algos, get_algo, list_algos
from aqi.constants import (
    ALGO_EPA,
    ALGO_EPA_2012,
    ALGO_EPA_2015,
    ALGO_EPA_2024,
    ALGO_MEP,
    ALGO_MEP_2012,
    ALGO_MEP_2026,
    POLLUTANT_CO_1H,
    POLLUTANT_CO_8H,
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
from aqi.exceptions import InsufficientDataError, NotApplicableError, OutOfRangeError
from aqi.nowcast import nowcast

__author__ = 'Stefan "hr" Berder'
__contact__ = "hr@bonz.org"
__license__ = "BSD 3-Clause"
__version__ = "1.0.0"

# the pollutant and algorithm constants are part of the public API
__all__ = [
    "ALGO_EPA",
    "ALGO_EPA_2012",
    "ALGO_EPA_2015",
    "ALGO_EPA_2024",
    "ALGO_MEP",
    "ALGO_MEP_2012",
    "ALGO_MEP_2026",
    "InsufficientDataError",
    "NotApplicableError",
    "OutOfRangeError",
    "POLLUTANT_CO_1H",
    "POLLUTANT_CO_8H",
    "POLLUTANT_CO_24H",
    "POLLUTANT_NO2_1H",
    "POLLUTANT_NO2_24H",
    "POLLUTANT_O3_1H",
    "POLLUTANT_O3_8H",
    "POLLUTANT_PM10",
    "POLLUTANT_PM25",
    "POLLUTANT_SO2_1H",
    "POLLUTANT_SO2_24H",
    "available_algos",
    "console_aqi",
    "get_algo",
    "list_algos",
    "to_aqi",
    "to_cc",
    "to_iaqi",
    "to_nowcast",
    "to_nowcast_aqi",
]


def _load_algo(algo):
    _aqi = get_algo(algo)
    if _aqi is None:
        raise ValueError(
            f"Unknown algorithm {algo!r}, available: {', '.join(available_algos())}"
        )
    return _aqi


def to_iaqi(elem, cc, algo=ALGO_EPA, extrapolate=False):
    """Calculate an intermediate AQI for a given pollutant. This is the
    heart of the algo.

    .. warning:: the concentration is passed as a string so
        :class:`decimal.Decimal` doesn't act up with binary floats.

    :param elem: pollutant constant
    :type elem: int
    :param cc: pollutant concentration (µg/m³ or ppm)
    :type cc: str
    :param algo: algorithm, ``'epa'`` for the latest version of a family,
                 ``'epa:2012'`` for a given version, or a module name like
                 ``'aqi.algos.epa'`` (latest version)
    :type algo: str
    :param extrapolate: compute values beyond the scale when the standard
                        describes how (EPA "Beyond the AQI")
    :type extrapolate: bool
    :raises OutOfRangeError: the concentration is not covered by the algorithm
    """
    _aqi = _load_algo(algo)
    return _aqi.iaqi(elem, cc, extrapolate=extrapolate)


def to_aqi(ccs, algo=ALGO_EPA, extrapolate=False):
    """Calculate the AQI based on a list of pollutants

    :param ccs: a list of tuples of pollutants concentrations with
                pollutant constant and concentration as values
    :type ccs: list
    :param algo: algorithm, see :func:`to_iaqi`
    :type algo: str
    :param extrapolate: see :func:`to_iaqi`
    :type extrapolate: bool
    :raises OutOfRangeError: a concentration is not covered by the algorithm
    """
    _aqi = _load_algo(algo)
    return _aqi.aqi(ccs, extrapolate=extrapolate)


def to_cc(elem, iaqi, algo=ALGO_EPA, extrapolate=False):
    """Calculate a concentration for a given pollutant.

    .. warning:: the intermediate AQI is passed as a string

    :param elem: pollutant constant
    :type elem: int
    :param iaqi: intermediate AQI
    :type iaqi: str
    :param algo: algorithm, ``'epa'`` for the latest version of a family,
                 ``'epa:2012'`` for a given version, or a module name like
                 ``'aqi.algos.epa'`` (latest version)
    :type algo: str
    :param extrapolate: see :func:`to_iaqi`
    :type extrapolate: bool
    :raises OutOfRangeError: the AQI value is not covered by the algorithm
    """
    _aqi = _load_algo(algo)
    return _aqi.cc(elem, iaqi, extrapolate=extrapolate)


def to_nowcast(elem, hourly, hours=12, min_weight="0.5"):
    """Calculate the NowCast concentration of PM2.5 or PM10 from hourly
    readings, see :func:`aqi.nowcast.nowcast`.

    :param elem: ``POLLUTANT_PM25`` or ``POLLUTANT_PM10``
    :type elem: str
    :param hourly: concentrations as strings (µg/m³), oldest first, the last
                   one is the current hour, ``None`` for a missing hour
    :type hourly: list
    :param hours: length of the window, 12 in the standard, at least 3
    :type hours: int
    :param min_weight: lower limit of the weight factor, 0.5 in the standard
                       (a string between 0 and 1)
    :type min_weight: str
    :return: the concentration, to be converted with :func:`to_iaqi`
    :rtype: decimal.Decimal
    :raises ValueError: no NowCast for this pollutant, window under 3 hours
    :raises OutOfRangeError: a reading is negative
    :raises InsufficientDataError: less than 2 of the last 3 hours are valid
    """
    return nowcast(elem, hourly, hours=hours, min_weight=min_weight)


def to_nowcast_aqi(
    series,
    hours=12,
    algo=ALGO_EPA,
    iaqis=False,
    extrapolate=False,
    min_weight="0.5",
):
    """Calculate the AQI of the NowCast of PM2.5 and PM10.

    The NowCast only aggregates concentrations, the index is computed by the
    algorithm, any algorithm works (EPA, MEP...). All the NowCast
    concentrations are given to it at once.

    :param series: a list of ``(pollutant, hourly readings)``, PM2.5 and PM10
                   only, see :func:`to_nowcast`
    :type series: list
    :param hours: length of the window, see :func:`to_nowcast`
    :type hours: int
    :param min_weight: see :func:`to_nowcast`
    :type min_weight: str
    :param algo: algorithm, see :func:`to_iaqi`
    :type algo: str
    :param iaqis: return a tuple of the AQI and a dict of the IAQIs
    :type iaqis: bool
    :param extrapolate: see :func:`to_iaqi`
    :type extrapolate: bool
    :raises InsufficientDataError: less than 2 of the last 3 hours of a series
                                   are valid
    """
    _aqi = _load_algo(algo)
    nowcasts = [
        (elem, str(nowcast(elem, hourly, hours=hours, min_weight=min_weight)))
        for elem, hourly in series
    ]
    return _aqi.aqi(nowcasts, iaqis=iaqis, extrapolate=extrapolate)


def console_aqi():
    """Console entry point, this function is used as an entry point to
    the 'aqi' command.
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="""Convert between AQI value and pollutant concentration (µg/m³ or
    ppm)."""
    )
    parser.add_argument(
        "-c",
        dest="conv",
        choices=["aqi", "cc"],
        default="aqi",
        help="Conversion to perform, defaults to 'aqi'",
    )
    parser.add_argument(
        "-l",
        action="store_true",
        dest="list",
        help="list the available algorithm versions and corresponding pollutants",
    )
    parser.add_argument(
        "-v", action="store_true", dest="verbose", help="add IAQIs to the result"
    )
    parser.add_argument(
        "-e",
        action="store_true",
        dest="extrapolate",
        help="compute values beyond the AQI scale when the standard allows it "
        "(EPA 'Beyond the AQI'), otherwise out of range values are an error",
    )
    parser.add_argument(
        "algo",
        nargs="?",
        help="the formula to use for the AQI calculation: a family and version "
        "like 'epa:2012', a family like 'epa' for its latest version, or the "
        "python module path",
    )
    parser.add_argument(
        "measures",
        nargs="*",
        metavar="measure",
        help="pollutant measure, format is "
        "element_name:concentration. Unknown "
        "pollutants are silently ignored.",
    )
    args = parser.parse_args()

    # list available algorithms
    if args.list is True:
        latest = {}
        for name in available_algos():
            latest[name.split(":")[0]] = name
        for name, pollutants in list_algos():
            elems = ", ".join(f"{elem} ({unit})" for elem, unit in pollutants)
            note = " (latest)" if name in latest.values() else ""
            print(f"{name}{note}: {elems}")
    else:
        # if not listing but missing other positional argument
        if args.algo is None or args.measures is None:
            sys.stderr.write("Missing algorithm or measure.\n")
            parser.print_help()
            sys.exit(1)
        _aqi = get_algo(args.algo)
        # couln't load the algo module or instanciate AQI class
        if _aqi is None:
            sys.stderr.write("Unknown algorithm or module is missing an AQI class\n")
            parser.print_help()
            sys.exit(1)
        try:
            if args.conv == "aqi":
                ccs = []
                for measure in args.measures:
                    (elem, cc) = measure.split(":")
                    ccs.append((elem, cc))

                ret = _aqi.aqi(ccs, iaqis=args.verbose, extrapolate=args.extrapolate)
                if args.verbose is True:
                    iaqis = []
                    for constant, iaqi in ret[1].items():
                        iaqis.append(constant + ":" + str(iaqi))
                    sys.stdout.write(" ".join(iaqis) + "\n")
                    sys.stdout.write(str(ret[0]) + "\n")
                else:
                    sys.stdout.write(str(ret) + "\n")
            else:
                iaqis = []
                for measure in args.measures:
                    (elem, iaqi) = measure.split(":")
                    iaqis.append((elem, iaqi))

                ret = []
                for iaqi in iaqis:
                    ret.append(
                        (
                            iaqi[0],
                            _aqi.cc(iaqi[0], iaqi[1], extrapolate=args.extrapolate),
                        )
                    )
                if len(ret) == 1:
                    sys.stdout.write(str(ret[0][1]) + "\n")
                elif len(ret) > 1:
                    ccs = []
                    for elem, cc in ret:
                        if cc is None:
                            ccs.append(elem + ":na")
                        else:
                            ccs.append(elem + ":" + str(cc))
                    sys.stdout.write("\n".join(ccs) + "\n")
        except OutOfRangeError as err:
            sys.stderr.write(f"Out of range: {err}\n")
            sys.exit(3)

    # end the script without a problem
    sys.exit(0)
