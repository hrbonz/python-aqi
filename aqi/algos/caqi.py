# -*- coding: utf-8 -*-

from decimal import *

from aqi.constants import (POLLUTANT_PM25, POLLUTANT_PM10,
                           POLLUTANT_O3_1H, POLLUTANT_CO_8H, POLLUTANT_SO2_1H,
                           POLLUTANT_NO2_1H)
from aqi.algos.base import PiecewiseAQI


class AQI(PiecewiseAQI):
    """Implementation of the CAQI algorithm.
    """

    piecewise = {
        'aqi': [
            (Decimal(0), Decimal(24.99)),
            (Decimal(25), Decimal(49.99)),
            (Decimal(50), Decimal(74.99)),
            (Decimal(75), Decimal(99.99)),
            (Decimal(100), Decimal(1000))],
        'bp': {
            POLLUTANT_NO2_1H: [
                (Decimal('0'), Decimal('49.99')),
                (Decimal('50'), Decimal('99.99')),
                (Decimal('100'), Decimal('199.99')),
                (Decimal('200'), Decimal('399.99')),
                (Decimal('400'), Decimal('inf')),
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
                (Decimal('25.01'), Decimal('50')),
                (Decimal('50.01'), Decimal('90')),
                (Decimal('90.01'), Decimal('180')),
                (Decimal('180.01'), Decimal('inf')),
            ],
            POLLUTANT_PM25: [
                (Decimal('0.0'), Decimal('15.0')),
                (Decimal('15.01'), Decimal('30.0')),
                (Decimal('30.01'), Decimal('55.0')),
                (Decimal('55.01'), Decimal('110.0')),
                (Decimal('110.01'), Decimal('inf')),
            ],
            POLLUTANT_CO_8H: [
                (Decimal('0.0'), Decimal('5000.0')),
                (Decimal('5000.01'), Decimal('7500.0')),
                (Decimal('7500.01'), Decimal('10000.0')),
                (Decimal('10000.01'), Decimal('20000.0')),
                (Decimal('20000.01'), Decimal('inf')),
            ],
            POLLUTANT_SO2_1H: [
                (Decimal('0'), Decimal('50')),
                (Decimal('50.01'), Decimal('100')),
                (Decimal('100.01'), Decimal('350')),
                (Decimal('350.01'), Decimal('500')),
                (Decimal('500.01'), Decimal('inf')),
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
