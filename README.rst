###########################
python-aqi - AQI conversion
###########################

A library to convert between AQI value and pollutant concentration
(µg/m³ or ppm) using the following algorithms:

* United States Environmental Protection Agency (EPA)
* China Ministry of Environmental Protection (MEP)

.. image:: https://travis-ci.org/hrbonz/python-aqi.svg?branch=master
    :target: https://travis-ci.org/hrbonz/python-aqi
    :alt: Testing Status

.. image:: https://readthedocs.org/projects/python-aqi/badge/?version=latest
    :target: https://readthedocs.org/projects/python-aqi/?badge=latest
    :alt: Documentation Status

.. image:: http://img.shields.io/badge/license-BSD%203--Clause-blue.svg
    :target: http://opensource.org/licenses/BSD-3-Clause
    :alt: license BSD 3-Clause


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
    aqi.algos.epa: pm10 (µg/m³), o3_8h (ppm), co_8h (ppm), no2_1h (ppb), o3_1h (ppm), so2_1h (ppb), pm25 (µg/m³)
    aqi.algos.mep: no2_24h (µg/m³), so2_24h (µg/m³), no2_1h (µg/m³), pm10 (µg/m³), o3_1h (µg/m³), o3_8h (µg/m³), so2_1h (µg/m³), co_1h (mg/m³), pm25 (µg/m³), co_24h (mg/m³)

Convert PM2.5 to IAQI using EPA algorithm::

    $ aqi aqi.algos.epa pm25:12
    39

Convert pollutants concentrations to AQI using EPA algorithm::

    $ aqi aqi.algos.epa pm25:40.9 o3_8h:0.077 co_1h:8.4
    104

Convert pollutants concentrations to AQI using EPA algorithm, display IAQIs::

    $ aqi -v aqi.algos.epa pm25:40.9 o3_8h:0.077 co_1h:8.4
    pm25:102 o3_8h:104 co_1h:90
    104


Development
===========

To install the development environment::

    $ pip install -r dev_requirements.txt


Test
====

Test the package::

    $ python -m unittest discover

Automatic testing in various environments::

    $ tox


Release
=======

Use `bumpr` to release the package::

    $ bumpr -b -m


Project
=======

* `Source code on github <https://github.com/hrbonz/python-aqi>`_
* `Documentation on readthedocs <http://python-aqi.readthedocs.org/>`_
* `Package on pypi <https://pypi.python.org/pypi/python-aqi>`_


Resources
=========

* EPA AQI: Technical Assistance Document for the Reporting of Daily Air
  Quality – the Air Quality Index (AQI) December 2013) found at http://www.epa.gov/airnow/aqi-technical-assistance-document-dec2013.pdf
* National Ambient Air Quality Standards for Particulate Matter found at http://www.gpo.gov/fdsys/pkg/FR-2013-01-15/pdf/2012-30946.pdf
* MEP AQI:

    * GB3095—2012 (2012/02/29) found at http://www.mep.gov.cn/gkml/hbb/bwj/201203/t20120302_224147.htm
    * HJ633-2012 (2012/02/29) found at http://www.zzemc.cn/em_aw/Content/HJ633-2012.pdf


License
=======

python-aqi is published under a BSD 3-clause license, see the LICENSE file
distributed with the project.
