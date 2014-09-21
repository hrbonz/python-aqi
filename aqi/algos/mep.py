# -*- coding: utf-8 -*-

from decimal import *

from aqi.constants import (POLLUTANT_PM25, POLLUTANT_PM10,
                          POLLUTANT_O3_8H, POLLUTANT_O3_1H,
                          POLLUTANT_CO_1H, POLLUTANT_CO_24H,
                          POLLUTANT_SO2_1H, POLLUTANT_SO2_24H,
                          POLLUTANT_NO2_1H, POLLUTANT_NO2_24H)
from aqi.algos.base import PiecewiseAQI


class AQI(PiecewiseAQI):
    """Implementation of the MEP AQI algorithm.
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
            POLLUTANT_SO2_24H: [
                (Decimal('0.0'), Decimal('50')),
                (Decimal('51'), Decimal('150')),
                (Decimal('151'), Decimal('475')),
                (Decimal('476'), Decimal('800')),
                (Decimal('801'), Decimal('1600')),
                (Decimal('1601'), Decimal('2100')),
                (Decimal('2101'), Decimal('2620')),
            ],
            POLLUTANT_SO2_1H: [
                (Decimal('0.0'), Decimal('150')),
                (Decimal('151'), Decimal('500')),
                (Decimal('501'), Decimal('650')),
                (Decimal('651'), Decimal('800')),
            ],
            POLLUTANT_NO2_24H: [
                (Decimal('0.0'), Decimal('40')),
                (Decimal('41'), Decimal('80')),
                (Decimal('81'), Decimal('180')),
                (Decimal('181'), Decimal('280')),
                (Decimal('281'), Decimal('565')),
                (Decimal('566'), Decimal('750')),
                (Decimal('751'), Decimal('940')),
            ],
            POLLUTANT_NO2_1H: [
                (Decimal('0.0'), Decimal('100')),
                (Decimal('101'), Decimal('200')),
                (Decimal('201'), Decimal('700')),
                (Decimal('701'), Decimal('1200')),
                (Decimal('1201'), Decimal('2340')),
                (Decimal('2341'), Decimal('3090')),
                (Decimal('3091'), Decimal('3840')),
            ],
            POLLUTANT_PM10: [
                (Decimal('00'), Decimal('50')),
                (Decimal('51'), Decimal('150')),
                (Decimal('151'), Decimal('250')),
                (Decimal('251'), Decimal('350')),
                (Decimal('351'), Decimal('420')),
                (Decimal('421'), Decimal('500')),
                (Decimal('501'), Decimal('600')),
            ],
            POLLUTANT_CO_24H: [
                (Decimal('0.0'), Decimal('2')),
                (Decimal('3'), Decimal('4')),
                (Decimal('5'), Decimal('14')),
                (Decimal('15'), Decimal('24')),
                (Decimal('25'), Decimal('36')),
                (Decimal('37'), Decimal('48')),
                (Decimal('49'), Decimal('60')),
            ],
            POLLUTANT_CO_1H: [
                (Decimal('0.0'), Decimal('5')),
                (Decimal('6'), Decimal('10')),
                (Decimal('11'), Decimal('35')),
                (Decimal('36'), Decimal('60')),
                (Decimal('61'), Decimal('90')),
                (Decimal('91'), Decimal('120')),
                (Decimal('121'), Decimal('150')),
            ],
            POLLUTANT_O3_1H: [
                (Decimal('0.0'), Decimal('160')),
                (Decimal('161'), Decimal('200')),
                (Decimal('201'), Decimal('300')),
                (Decimal('301'), Decimal('400')),
                (Decimal('401'), Decimal('800')),
                (Decimal('801'), Decimal('1000')),
                (Decimal('1001'), Decimal('1200')),
            ],
            POLLUTANT_O3_8H: [
                (Decimal('0.0'), Decimal('100')),
                (Decimal('101'), Decimal('160')),
                (Decimal('161'), Decimal('215')),
                (Decimal('216'), Decimal('265')),
                (Decimal('266'), Decimal('800')),
            ],
            POLLUTANT_PM25: [
                (Decimal('0.0'), Decimal('35')),
                (Decimal('36'), Decimal('75')),
                (Decimal('76'), Decimal('115')),
                (Decimal('116'), Decimal('150')),
                (Decimal('151'), Decimal('250')),
                (Decimal('251'), Decimal('350')),
                (Decimal('351'), Decimal('500')),
            ],
        },
        'prec': {
            POLLUTANT_O3_8H: Decimal('1.'),
            POLLUTANT_O3_1H: Decimal('1.'),
            POLLUTANT_PM10: Decimal('1.'),
            POLLUTANT_PM25: Decimal('1.'),
            POLLUTANT_CO_1H: Decimal('1.'),
            POLLUTANT_CO_24H: Decimal('1.'),
            POLLUTANT_SO2_1H: Decimal('1.'),
            POLLUTANT_SO2_24H: Decimal('1.'),
            POLLUTANT_NO2_1H: Decimal('1.'),
            POLLUTANT_NO2_24H: Decimal('1.'),
        },
        'units': {
            POLLUTANT_SO2_24H: 'µg/m³',
            POLLUTANT_SO2_1H: 'µg/m³',
            POLLUTANT_NO2_24H: 'µg/m³',
            POLLUTANT_NO2_1H: 'µg/m³',
            POLLUTANT_PM10: 'µg/m³',
            POLLUTANT_CO_24H: 'mg/m³',
            POLLUTANT_CO_1H: 'mg/m³',
            POLLUTANT_O3_1H: 'µg/m³',
            POLLUTANT_O3_8H: 'µg/m³',
            POLLUTANT_PM25: 'µg/m³',
        },
    }
