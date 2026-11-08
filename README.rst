###########################
python-aqi - AQI conversion
###########################

A library to convert between AQI value and pollutant concentration
(µg/m³ or ppm) using the following algorithms:

* United States Environmental Protection Agency (EPA)
* China Ministry of Environmental Protection (MEP)

.. image:: https://github.com/hrbonz/python-aqi/actions/workflows/ci.yml/badge.svg?branch=master
    :target: https://github.com/hrbonz/python-aqi/actions/workflows/ci.yml
    :alt: Testing Status

.. image:: https://readthedocs.org/projects/python-aqi/badge/?version=latest
    :target: https://readthedocs.org/projects/python-aqi/?badge=latest
    :alt: Documentation Status

.. image:: http://img.shields.io/badge/license-BSD%203--Clause-blue.svg
    :target: http://opensource.org/licenses/BSD-3-Clause
    :alt: license BSD 3-Clause


Install
=======

With pip::

    $ pip install python-aqi

With `uv <https://docs.astral.sh/uv/>`_, to add it to a project::

    $ uv add python-aqi

or to install the ``aqi`` command line tool::

    $ uv tool install python-aqi


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

The algorithm is a standard and its version: ``'epa:2012'``, or ``'epa'`` for
the latest version of the family (``aqi.ALGO_EPA``, ``aqi.ALGO_EPA_2012`` and
the matching ``MEP`` constants are available). Old versions stay selectable, the
default is always the latest. ``aqi.available_algos()`` lists them all::

    aqi.available_algos()
    # ['epa:2012', 'epa:2015', 'epa:2024', 'mep:2012', 'mep:2026']

The EPA versions are named after the revision that changed the table:

* ``epa:2012``: what python-aqi computed until 0.6, PM2.5 Good up to 12.0
  µg/m³ and the 1997 ozone 8 hour breakpoints
* ``epa:2015``: new ozone 8 hour breakpoints (0.054, 0.070, 0.085, 0.105, 0.200
  ppm), 1 hour ozone only above 0.125 ppm
* ``epa:2024``: new PM2.5 breakpoints (Good up to 9.0 µg/m³) and a single
  Hazardous category, 301 to 500, for every pollutant. This is the default.

The MEP (China) versions follow the standards. The name ``MEP`` stands for the
Ministry of Environmental Protection, which published HJ 633-2012. The ministry
was renamed Ministry of Ecology and Environment (MEE) in 2018 and publishes
HJ 633-2026 under that name, the library keeps ``MEP`` for all versions so that
the name used by existing code does not change:

* ``mep:2012``: HJ 633-2012, laid out like the EPA tables as python-aqi always
  did
* ``mep:2026``: HJ 633-2026, effective 1 March 2026. The limits of IAQI 100
  change for PM10 (150 to 120 µg/m³) and PM2.5 (75 to 60 µg/m³), and the
  calculation follows the standard: IAQI interpolated between the limits of
  the table, IAQI and AQI rounded up, concentrations rounded to integers (CO to
  one decimal). This is the default for MEP.

``mep:2012`` is kept as it was, with its approximations (see ``MEP_2012``). The
default changed with the 2024 and 2026 versions: the same PM2.5 concentration can
now give a different AQI, ``aqi.to_iaqi(aqi.POLLUTANT_PM25, '12.1')`` is 57,
it was 51, and ``aqi.to_iaqi(aqi.POLLUTANT_PM25, '60', algo=aqi.ALGO_MEP)`` is
100, it was 81. Use ``algo=aqi.ALGO_EPA_2012`` or ``aqi.ALGO_MEP_2012`` to keep
the old results.

1 hour ozone has no value under 0.125 ppm in the EPA table. ``to_aqi`` ignores
it when other pollutants are given (the standard says to disregard it), for
``to_iaqi`` and ``to_cc`` it raises ``aqi.NotApplicableError``, an
``OutOfRangeError``.

Convert an IAQI to its pollutant concentration::

    import aqi
    mycc = aqi.to_cc(aqi.POLLUTANT_PM25, '22', algo=aqi.ALGO_EPA)

Out of range values
~~~~~~~~~~~~~~~~~~~

A concentration (or an AQI) that is not covered by the algorithm raises
``aqi.OutOfRangeError``, a subclass of ``ValueError`` that carries ``elem``,
``value``, ``low`` and ``high``. Values are never capped: a capped value would
hide how far above the scale a measure is, so what to do with it is up to the
calling code::

    try:
        myaqi = aqi.to_aqi([(aqi.POLLUTANT_PM25, '800')])
    except aqi.OutOfRangeError as err:
        print(err.elem, err.value, err.high)

The EPA calls AQI values above 500 "Beyond the AQI" and explains how to
compute them: use the regular formula with the Hazardous breakpoints. This is
available on request with ``extrapolate=True``::

    aqi.to_aqi([(aqi.POLLUTANT_PM25, '800')], extrapolate=True)  # 1445

This only applies to the EPA algorithm and to pollutants whose table covers
the whole scale. 8 hour ozone, for example, stops at 300 because the EPA uses
1 hour ozone above that. The MEP standard has no such method, so ``extrapolate=True``
still raises with it. HJ 633-2026 does fix the IAQI of two pollutants above
their table: SO2 1 hour above 800 µg/m³ is 200 and O3 8 hour above 800 µg/m³
is 300 (HJ 633-2012 said they are not computed, and ``mep:2012`` raises).


Command line
------------

List supported algorithms and pollutants::

    $ aqi -l
    epa:2012: o3_8h (ppm), o3_1h (ppm), pm10 (µg/m³), pm25 (µg/m³), co_8h (ppm), so2_1h (ppb), no2_1h (ppb)
    epa:2015: o3_8h (ppm), o3_1h (ppm), pm10 (µg/m³), pm25 (µg/m³), co_8h (ppm), so2_1h (ppb), no2_1h (ppb)
    epa:2024 (latest): o3_8h (ppm), o3_1h (ppm), pm10 (µg/m³), pm25 (µg/m³), co_8h (ppm), so2_1h (ppb), no2_1h (ppb)
    mep:2012: so2_24h (µg/m³), so2_1h (µg/m³), no2_24h (µg/m³), no2_1h (µg/m³), pm10 (µg/m³), co_24h (mg/m³), co_1h (mg/m³), o3_1h (µg/m³), o3_8h (µg/m³), pm25 (µg/m³)
    mep:2026 (latest): so2_24h (µg/m³), so2_1h (µg/m³), no2_24h (µg/m³), no2_1h (µg/m³), pm10 (µg/m³), co_24h (mg/m³), co_1h (mg/m³), o3_1h (µg/m³), o3_8h (µg/m³), pm25 (µg/m³)

Pick the version of a standard with ``family:version``, ``epa`` alone means the
latest version, the module names (``aqi.algos.epa``) still work and also mean
the latest::

    $ aqi epa:2012 pm25:12
    50

Convert PM2.5 to IAQI using EPA algorithm::

    $ aqi aqi.algos.epa pm25:12
    56

Convert PM2.5 to IAQI using EPA algorithm (full length)::

    $ aqi -c aqi aqi.algos.epa pm25:12
    56

Convert pollutants concentrations to AQI using EPA algorithm::

    $ aqi aqi.algos.epa pm25:40.9 o3_8h:0.077 co_8h:8.4
    122

Convert pollutants concentrations to AQI using EPA algorithm, display IAQIs::

    $ aqi -v aqi.algos.epa pm25:40.9 o3_8h:0.077 co_8h:8.4
    pm25:114 o3_8h:122 co_8h:90
    122

Convert PM2.5 IAQI to concentration using EPA algorithm::

    $ aqi -c cc aqi.algos.epa pm25:39
    7.0

Out of range values are an error, the message goes to stderr and the exit
code is 3::

    $ aqi aqi.algos.epa pm25:800
    Out of range: pm25: 800.0 is not covered by the algorithm (valid range is 0.0 to 325.4)

``-e`` computes EPA values beyond the scale ("Beyond the AQI")::

    $ aqi -e aqi.algos.epa pm25:800
    1445


Development
===========

Set up the development environment (ruff, pre-commit, hatch, coverage)::

    $ uv sync
    $ uv run pre-commit install

Code is linted and formatted with `ruff <https://docs.astral.sh/ruff/>`_
through `pre-commit <https://pre-commit.com/>`_, the checks run on each
commit. To run them on all files::

    $ uv run pre-commit run --all-files

Test the package::

    $ uv run python -m unittest discover

The same checks and the tests on Python 3.9 to 3.14 run on GitHub Actions
(``.github/workflows/ci.yml``) for each push and pull request.


Release
=======

Use `bumpr` to release the package::

    $ bumpr -b -m


Project
=======

* `Source code on github <https://github.com/hrbonz/python-aqi>`_
* `Documentation on readthedocs <https://python-aqi.readthedocs.io/>`_
* `Package on pypi <https://pypi.python.org/pypi/python-aqi>`_


Resources
=========

* EPA AQI: Technical Assistance Document for the Reporting of Daily Air
  Quality – the Air Quality Index (AQI) December 2013) found at http://www.epa.gov/airnow/aqi-technical-assistance-document-dec2013.pdf
* National Ambient Air Quality Standards for Particulate Matter found at http://www.gpo.gov/fdsys/pkg/FR-2013-01-15/pdf/2012-30946.pdf
* MEP AQI:

    * GB3095—2012 (2012/02/29) found at http://www.mep.gov.cn/gkml/hbb/bwj/201203/t20120302_224147.htm
    * HJ633-2012 (2012/02/29) found at https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/jcffbz/201203/W020120410332725219541.pdf


License
=======

python-aqi is published under a BSD 3-clause license, see the LICENSE file
distributed with the project.
