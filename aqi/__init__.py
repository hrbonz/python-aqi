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
from aqi.exceptions import NotApplicableError, OutOfRangeError

__author__ = 'Stefan "hr" Berder'
__contact__ = "hr@bonz.org"
__license__ = "BSD 3-Clause"
__version__ = "0.6.1"

# the pollutant and algorithm constants are part of the public API
__all__ = [
    "ALGO_EPA",
    "ALGO_EPA_2012",
    "ALGO_EPA_2015",
    "ALGO_EPA_2024",
    "ALGO_MEP",
    "ALGO_MEP_2012",
    "ALGO_MEP_2026",
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
    :param cc: intermediate AQI
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
