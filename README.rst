===========================
python-aqi - AQI conversion
===========================

A library to convert between AQI value and pollutant concentration
(µg/m³ or ppm) using the following algorithms:

* United States Environmental Protection Agency (EPA)
* China Ministry of Environmental Protection (MEP)

Usage
-----

::

    import aqi
    aqi = to_aqi(12, pollutant=aqi.POLLUTANT_PM25, algorithm=aqi.ALGO_EPA)

License
-------

python-aqi is published under a BSD 3-clause license, see the LICENSE file
distributed with the project.
