# -*- coding: utf-8 -*-

# constants for pollutants names
POLLUTANT_PM25 = 0
POLLUTANT_PM10 = 1
POLLUTANT_O3_8H = 2
POLLUTANT_O3_1H = 3
POLLUTANT_CO = 4
POLLUTANT_SO2 = 5
POLLUTANT_NO2 = 6

POLLUTANT_NAMES = {
    POLLUTANT_PM25: 'pm25',
    POLLUTANT_PM10: 'pm10',
    POLLUTANT_O3_8H: 'o3_8h',
    POLLUTANT_O3_1H: 'o3_1h',
    POLLUTANT_CO: 'co',
    POLLUTANT_SO2: 'so2',
    POLLUTANT_NO2: 'no2',
}

# constants for algorithms, canonical module name
ALGO_EPA = 'aqi.algos.epa'

def get_constant(name):
    """Get a pollutant constant based on its name, return a constant or
    None if the pollutant is unknown"""
    for (idx, _name) in POLLUTANT_NAMES.items():
        if name == _name:
            return idx
    return None
