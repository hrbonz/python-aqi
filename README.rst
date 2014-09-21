###########################
python-aqi - AQI conversion
###########################

A library to convert between AQI value and pollutant concentration
(µg/m³ or ppm) using the following algorithms:

* United States Environmental Protection Agency (EPA)
* China Ministry of Environmental Protection (MEP)

.. image:: https://travis-ci.org/hrbonz/python-aqi.svg?branch=master
    :target: https://travis-ci.org/hrbonz/python-aqi


Install
=======

::

    $ pip install python-aqi


Usage
=====

Library
-------

Convert a pollutant to its IAQI (Intermediate Air Quality Index)::

    import aqi
    myaqi = aqi.to_iaqi(aqi.POLLUTANT_PM25, '12', algo=aqi.ALGO_EPA)

Get an AQI out of several pollutant concentrations, default algorithm is EPA::

    import aqi
    myaqi = aqi.to_aqi([
        (aqi.POLLUTANT_PM25, '12'),
        (aqi.POLLUTANT_PM10, '24'),
        (aqi.POLLUTANT_O3_8H, '0.087')
    ])

Convert an IAQI to its pollutant concentration::

    import aqi
    mycc = aqi.to_cc(aqi.POLLUTANT_PM25, '22', algo=aqi.ALGO_EPA)


Command line
------------

List supported algorithms and pollutants::

    $ aqi -l
    aqi.algos.epa: pm25, pm10, o3_8h, o3_1h, co, so2, no2
    aqi.algos.mep: pm25, pm10, o3_8h, o3_1h, so2_24h, so2_1h, no2_24h, no2_1h, co_24h, co_1h

Convert PM2.5 to IAQI using EPA algorithm::

    $ aqi epa pm25:12
    39

Convert pollutants concentrations to AQI using EPA algorithm::

    $ aqi aqi.algos.epa pm25:40.9 o3_8h:0.077 co:8.4
    104

Convert pollutants concentrations to AQI using EPA algorithm, display IAQIs::

    $ aqi -v aqi.algos.epa pm25:40.9 o3_8h:0.077 co:8.4
    pm25:102 o3_8h:104 co:90
    104


Test
====

Test the package::

    $ python -m unittest discover


Resource
========

* EPA AQI: Technical Assistance Document for the Reporting of Daily Air
* Quality – the Air Quality Index (AQI) (September 2012) found at http://www.epa.gov/airnow/aqi-technical-assistance-document-sep2012.pdf
* MEP AQI:

    * GB3095—2012 (2012/02/29) found at http://www.mep.gov.cn/gkml/hbb/bwj/201203/t20120302_224147.htm
    * HJ633-2012 (2012/02/29) found at http://www.zzemc.cn/em_aw/Content/HJ633-2012.pdf

License
=======

python-aqi is published under a BSD 3-clause license, see the LICENSE file
distributed with the project.
