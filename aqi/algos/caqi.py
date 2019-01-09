# -*- coding: utf-8 -*-

from decimal import *

from aqi.constants import (POLLUTANT_PM25, POLLUTANT_PM10,
                           POLLUTANT_O3_1H, POLLUTANT_CO_8H, POLLUTANT_SO2_1H,
                           POLLUTANT_NO2_1H)
from aqi.algos.base import PiecewiseAQI


class AQI(PiecewiseAQI):
    """Implementation of the EPA AQI algorithm.
    """

    piecewise = {
        'aqi': [
            (0, 25),
            (26, 50),
            (51, 75),
            (76, 100),
            (101, 1000)],
        'bp': {
            POLLUTANT_NO2_1H: [
                (Decimal('0'), Decimal('50')),
                (Decimal('51'), Decimal('100')),
                (Decimal('101'), Decimal('200')),
                (Decimal('201'), Decimal('400')),
                (Decimal('401'), Decimal('inf')),
            ],
            POLLUTANT_O3_1H: [
                (Decimal('0.0'), Decimal('60.000')),
                (Decimal('60.001'), Decimal('120.000')),
                (Decimal('120.001'), Decimal('180.000')),
                (Decimal('180.001'), Decimal('240.000')),
                (Decimal('240.001'), Decimal('inf')),
            ],
            POLLUTANT_PM10: [
                (Decimal('0'), Decimal('25')),
                (Decimal('26'), Decimal('50')),
                (Decimal('51'), Decimal('90')),
                (Decimal('91'), Decimal('180')),
                (Decimal('181'), Decimal('inf')),
            ],
            POLLUTANT_PM25: [
                (Decimal('0.0'), Decimal('15.0')),
                (Decimal('15.1'), Decimal('30.0')),
                (Decimal('30.1'), Decimal('55.0')),
                (Decimal('55.1'), Decimal('110.0')),
                (Decimal('110.1'), Decimal('inf')),
            ],
            POLLUTANT_CO_8H: [
                (Decimal('0.0'), Decimal('5000.0')),
                (Decimal('5000.1'), Decimal('7500.0')),
                (Decimal('7500.1'), Decimal('10000.0')),
                (Decimal('10000.1'), Decimal('20000.0')),
                (Decimal('20000.1'), Decimal('inf')),
            ],
            POLLUTANT_SO2_1H: [
                (Decimal('0'), Decimal('50')),
                (Decimal('51'), Decimal('100')),
                (Decimal('101'), Decimal('350')),
                (Decimal('351'), Decimal('500')),
                (Decimal('501'), Decimal('inf')),
            ],
        },
        'prec': {
            POLLUTANT_O3_1H: Decimal('.001'),
            POLLUTANT_PM10: Decimal('.1'),
            POLLUTANT_PM25: Decimal('.1'),
            POLLUTANT_CO_8H: Decimal('.1'),
            POLLUTANT_SO2_1H: Decimal('1.'),
            POLLUTANT_NO2_1H: Decimal('1.'),
        },
        'units': {
            POLLUTANT_O3_1H: 'µg/m³',
            POLLUTANT_PM10: 'µg/m³',
            POLLUTANT_PM25: 'µg/m³',
            POLLUTANT_CO_8H: 'µg/m³',
            POLLUTANT_SO2_1H: 'µg/m³',
            POLLUTANT_NO2_1H: 'µg/m³',
        },
    }
