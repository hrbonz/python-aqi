# -*- coding: utf-8 -*-

from aqi.constants import (POLLUTANT_PM25, POLLUTANT_PM10,
                          POLLUTANT_O3_8H, POLLUTANT_O3_1H,
                          POLLUTANT_CO, POLLUTANT_SO2, POLLUTANT_NO2,
                          ALGO_EPA)

from aqi.algos import get_algo

__author__ = "Stefan \"hr\" Berder"
__contact__ = "hr@bonz.org"
__license__ = "BSD 3-Clause"
__version__ = "v0.2"


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
