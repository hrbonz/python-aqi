# -*- coding: utf-8 -*-

import argparse

from aqi.constants import (POLLUTANT_PM25, POLLUTANT_PM10,
                          POLLUTANT_O3_8H, POLLUTANT_O3_1H,
                          POLLUTANT_CO, POLLUTANT_SO2, POLLUTANT_NO2,
                          ALGO_EPA)

from aqi.algos import get_algo, list_algos

__author__ = "Stefan \"hr\" Berder"
__contact__ = "hr@bonz.org"
__license__ = "BSD 3-Clause"
__version__ = "v0.3"


def to_iaqi(elem, cc, algo=ALGO_EPA):
    """Calculate an intermediate AQI for a given pollutant. This is the
    heart of the algo.

    .. warning:: the concentration is passed as a string so
        :class:`decimal.Decimal` doesn't act up with binary floats.

    :param elem: pollutant constant
    :type elem: int
    :param cc: pollutant contentration (µg/m³ or ppm)
    :type cc: str
    :param algo: algorithm module canonical name
    :type algo: str
    """
    _aqi = get_algo(algo)
    return _aqi.iaqi(elem, cc)

def to_aqi(ccs, algo=ALGO_EPA):
    """Calculate the AQI based on a list of pollutants

    :param ccs: a list of tuples of pollutants concentrations with
                pollutant constant and concentration as values
    :type ccs: list
    :param algo: algorithm module name
    :type algo: str
    """
    _aqi = get_algo(algo)
    return _aqi.aqi(ccs)

def console_aqi():
    """Console entry point, this functionis used as an entry point to
    the 'aqi' command.
    """
    import sys
    import argparse

    parser = argparse.ArgumentParser(description=
    """Convert between AQI value and pollutant concentration (µg/m³ or
    ppm).""")
    parser.add_argument('-l', action='store_true', dest='list',
                        help='list the available algorithms and '
                             'corresponding pollutants')
    args = parser.parse_args()

    if args.list is True:
        for _algo in list_algos():
            print("{algo}: {elem}".format(algo=_algo[0],
                                          elem=', '.join(_algo[1])))
        sys.exit(0)

    # end the script wihtout any argument
    sys.exit(0)
