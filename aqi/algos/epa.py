# -*- coding: utf-8 -*-

from decimal import *

from aqi.constants import (POLLUTANT_PM25, POLLUTANT_PM10,
                          POLLUTANT_O3_8H, POLLUTANT_O3_1H,
                          POLLUTANT_CO_8H, POLLUTANT_SO2_1H,
                          POLLUTANT_NO2_1H)
from aqi.algos.base import PiecewiseAQI


class AQI(PiecewiseAQI):
    """Implementation of the EPA AQI algorithm.
    """

    piecewise = {
        'aqi': [
            (0, 50),
            (51, 100),
            (101, 150),
            (151, 200),
            (201, 300),
            (301, 400),
            (401, 500)],
        'bp': {
            POLLUTANT_O3_8H: [
                (Decimal('0.000'), Decimal('0.059')),
                (Decimal('0.060'), Decimal('0.075')),
                (Decimal('0.076'), Decimal('0.095')),
                (Decimal('0.096'), Decimal('0.115')),
                (Decimal('0.116'), Decimal('0.374')),
            ],
            POLLUTANT_O3_1H: [
                (0, 0),
                (0, 0),
                (Decimal('0.125'), Decimal('0.164')),
                (Decimal('0.165'), Decimal('0.204')),
                (Decimal('0.205'), Decimal('0.404')),
                (Decimal('0.405'), Decimal('0.504')),
                (Decimal('0.505'), Decimal('0.604')),
            ],
            POLLUTANT_PM10: [
                (Decimal('0'), Decimal('54')),
                (Decimal('55'), Decimal('154')),
                (Decimal('155'), Decimal('254')),
                (Decimal('255'), Decimal('354')),
                (Decimal('355'), Decimal('424')),
                (Decimal('425'), Decimal('504')),
                (Decimal('505'), Decimal('604')),
            ],
            POLLUTANT_PM25: [
                (Decimal('0.0'), Decimal('12.0')),
                (Decimal('12.1'), Decimal('35.4')),
                (Decimal('35.5'), Decimal('55.4')),
                (Decimal('55.5'), Decimal('150.4')),
                (Decimal('150.5'), Decimal('250.4')),
                (Decimal('250.5'), Decimal('350.4')),
                (Decimal('350.5'), Decimal('500.4')),
            ],
            POLLUTANT_CO_8H: [
                (Decimal('0.0'), Decimal('4.4')),
                (Decimal('4.5'), Decimal('9.4')),
                (Decimal('9.5'), Decimal('12.4')),
                (Decimal('12.5'), Decimal('15.4')),
                (Decimal('15.5'), Decimal('30.4')),
                (Decimal('30.5'), Decimal('40.4')),
                (Decimal('40.5'), Decimal('50.4')),
            ],
            POLLUTANT_SO2_1H: [
                (Decimal('0'), Decimal('35')),
                (Decimal('36'), Decimal('75')),
                (Decimal('76'), Decimal('185')),
                (Decimal('186'), Decimal('304')),
                (Decimal('305'), Decimal('604')),
                (Decimal('605'), Decimal('804')),
                (Decimal('805'), Decimal('1004')),
            ],
            POLLUTANT_NO2_1H: [
                (Decimal('0'), Decimal('53')),
                (Decimal('54'), Decimal('100')),
                (Decimal('101'), Decimal('360')),
                (Decimal('361'), Decimal('649')),
                (Decimal('650'), Decimal('1249')),
                (Decimal('1250'), Decimal('1649')),
                (Decimal('1650'), Decimal('2049')),
            ],
        },
        'prec': {
            POLLUTANT_O3_8H: Decimal('.001'),
            POLLUTANT_O3_1H: Decimal('.001'),
            POLLUTANT_PM10: Decimal('1.'),
            POLLUTANT_PM25: Decimal('.1'),
            POLLUTANT_CO_8H: Decimal('.1'),
            POLLUTANT_SO2_1H: Decimal('1.'),
            POLLUTANT_NO2_1H: Decimal('1.'),
        },
        'units': {
            POLLUTANT_O3_8H: 'ppm',
            POLLUTANT_O3_1H: 'ppm',
            POLLUTANT_PM10: 'µg/m³',
            POLLUTANT_PM25: 'µg/m³',
            POLLUTANT_CO_8H: 'ppm',
            POLLUTANT_SO2_1H: 'ppb',
            POLLUTANT_NO2_1H: 'ppb',
        },
    }
