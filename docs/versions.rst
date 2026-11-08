Standards and versions
======================

An air quality index is defined by a standard, and standards get revised when
the health evidence changes. python-aqi keeps every version it knows: pick one
with ``algo='epa:2024'``, ``algo='mep:2026'``... or leave the default, which is
always the **latest** version of the family (``'epa'``, ``'mep'``).

``aqi.available_algos()`` lists the versions and ``aqi -l`` does the same on
the command line. The PDFs behind every table are archived in
:doc:`standards/index`.

.. contents::
   :local:
   :depth: 2

EPA (United States)
-------------------

The EPA AQI is defined by 40 CFR Part 58 Appendix G and explained in the
*Technical Assistance Document for the Reporting of Daily Air Quality* (TAD).
A version is named after the revision that changed the table.

.. list-table::
   :header-rows: 1
   :widths: 10 36 30 24

   * - Version
     - What changed
     - Rule
     - Source of the table
   * - ``epa:2012``
     - PM2.5 annual standard lowered to 12 µg/m³ (Good up to 12.0). Ozone
       8 hour breakpoints still those of 1997 (0.059, 0.075, 0.095, 0.115).
       This is what python-aqi computed until 0.6.
     - 78 FR 3086, published 2013-01-15, effective 2013-03-18
     - TAD EPA-454/B-13-001 (December 2013) and 78 FR 3286
   * - ``epa:2015``
     - Ozone standard lowered to 0.070 ppm: new 8 hour ozone breakpoints
       (0.054, 0.070, 0.085, 0.105, 0.200). 1 hour ozone only above
       0.125 ppm.
     - 80 FR 65292, published 2015-10-26, effective 2015-12-28
     - TAD EPA-454/B-18-007 (September 2018)
   * - ``epa:2024``
     - PM2.5 annual standard lowered to 9 µg/m³: new PM2.5 breakpoints (Good up
       to 9.0). A single Hazardous category, 301 to 500, for every pollutant.
     - 89 FR 16202, published 2024-03-06, effective 2024-05-06
     - TAD EPA-403/B-26-003 (May 2026), same table as EPA-454/B-24-002
       (May 2024)

The "Rule" column is the final rule that revised the national ambient air
quality standard, the AQI follows it. Only the effective date of
``epa:2012`` is stated in the archived documents (78 FR 3086); the other dates
come from the Federal Register.

Concentrations are truncated to the precision of the pollutant (ozone 3
decimals, PM2.5 and CO 1, the others integers) before the calculation, as the
TAD says, and the result is rounded to the nearest integer.

epa:2012
~~~~~~~~

.. aqi-breakpoints:: epa:2012

Known flaw, kept for compatibility: the first two bands of 1 hour ozone are
``(0, 0)`` (issue 15). The later versions leave them blank.

epa:2015
~~~~~~~~

.. aqi-breakpoints:: epa:2015

Hazardous is split in two bands (301-400 and 401-500) like in 2012.

epa:2024
~~~~~~~~

.. aqi-breakpoints:: epa:2024

Hazardous is a single band, 301-500, and its top is the concentration of AQI
500 (PM2.5 325.4 µg/m³). For PM10, CO, SO2, NO2 and 1 hour ozone this replaces
the two Hazardous bands of the earlier versions: PM10 504 µg/m³ is 400 in
``epa:2015`` and 389 in ``epa:2024``.

1 hour ozone has no value under 0.125 ppm and 8 hour ozone none above 0.200
ppm (AQI 300), the standard says to use the other one there. A blank in the
table is :class:`aqi.NotApplicableError` for a single pollutant, and
:func:`aqi.to_aqi` ignores that pollutant when others are given.

MEP (China)
-----------

The Chinese index is HJ 633, *Technical specifications on ambient air quality
index*. The name ``MEP`` is kept for all the versions, although the ministry
that publishes it is now called MEE (see :doc:`standards/index`).

.. list-table::
   :header-rows: 1
   :widths: 10 40 26 24

   * - Version
     - What changed
     - Dates
     - Source of the table
   * - ``mep:2012``
     - HJ 633-2012, "on trial". Kept as python-aqi always computed it.
     - published 2012-02-29, in force from 2016-01-01, repealed
       2026-03-01
     - HJ 633-2012, table 1
   * - ``mep:2026``
     - HJ 633-2026. The PM10 and PM2.5 limits of IAQI 100 are lowered (150 to
       120 and 75 to 60 µg/m³). The calculation follows the standard.
     - published 2026-02-14, in force from 2026-03-01
     - HJ 633-2026, table 3

The tables show the concentration range of each band of the scale.

mep:2012
~~~~~~~~

.. aqi-breakpoints:: mep:2012

This version lays the tables out like the EPA ones (a gap between two bands,
concentrations truncated to integers, IAQI rounded half to even). That is not
what HJ 633-2012 says, which is why ``mep:2026`` is built differently. 8 hour
ozone above 800 µg/m³ and 1 hour SO2 above 800 µg/m³ are "not computed": they
raise :class:`aqi.OutOfRangeError`.

mep:2026
~~~~~~~~

.. aqi-breakpoints:: mep:2026

The formula of the standard interpolates between neighbouring limits of
table 3, so a band starts where the previous one ends. The concentration limit
of each IAQI is in the :doc:`transcription <standards/hj633-2026-table>`.

* Concentrations are rounded (GB/T 8170: to the nearest, an exact 5 goes to the
  even digit) to integers, CO to one decimal.
* IAQI and AQI are **rounded up** to an integer.
* SO2 1 hour above 800 µg/m³ is IAQI 200, and 8 hour ozone above 800 µg/m³ is
  IAQI 300.
* The 1 hour limits of SO2, NO2, CO and O3 are for real time reports only,
  daily reports use the 24 hour (8 hour for ozone) pollutants.

.. _upgrading-from-0.6:

Upgrading from 0.6
------------------

The default algorithm used to be the one version the library had, it is now the
latest version, and the numbers can differ:

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Call
     - 0.6
     - Now
   * - ``to_iaqi('pm25', '12.1')``
     - 51
     - 57
   * - ``to_iaqi('o3_8h', '0.060')``
     - 51
     - 67
   * - ``to_iaqi('pm25', '60', algo=ALGO_MEP)``
     - 81
     - 100
   * - ``to_iaqi('pm10', '60', algo=ALGO_MEP)``
     - 55
     - 58

To keep the previous results, name the version::

    import aqi
    aqi.to_iaqi(aqi.POLLUTANT_PM25, '12.1', algo=aqi.ALGO_EPA_2012)
    aqi.to_aqi(ccs, algo=aqi.ALGO_MEP_2012)

``epa:2012`` and ``mep:2012`` give exactly the 0.6.1 results, this is checked
against the output of 0.6.1 by the test suite. Pin the version in code that
publishes an index, the default will follow the next revision of a standard.

Also new: values outside of a standard's table raise
:class:`aqi.OutOfRangeError` instead of ``IndexError`` or a wrong number, see
the README. ``algo=`` raises ``ValueError`` for an unknown algorithm.
