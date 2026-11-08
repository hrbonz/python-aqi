How an AQI is computed
======================

This page answers the questions that come back most often: what the numbers
mean, which averages to feed the library and what it does not do.

IAQI and AQI
------------

Every pollutant has its own index, the *individual air quality index*, IAQI
(the EPA says "sub-index"; the README and the API say "intermediate AQI"). It is
a piecewise linear function of the concentration: the standard gives a table of
concentration limits for the index values 0, 50, 100... 500 and the IAQI is
interpolated between the two limits around the concentration.

The **AQI** is the highest IAQI of the pollutants that were measured, and the
pollutant that gives it is the *primary pollutant*.

* :func:`aqi.to_iaqi` converts the concentration of one pollutant,
* :func:`aqi.to_aqi` takes the concentrations of several pollutants and returns
  the highest IAQI (``iaqis=True`` on the algorithm class also returns the
  IAQI of each pollutant),
* :func:`aqi.to_cc` goes the other way, from an index value to a concentration.

Which average to give
---------------------

A standard works on averages, not on raw readings. The pollutant constants name
the averaging time, and python-aqi expects the value **already averaged**, as a
string (so that no binary float gets in the way):

* EPA: PM2.5 and PM10 24 hour averages, ozone daily maximum of the 8 hour
  averages (``o3_8h``, and optionally the 1 hour value ``o3_1h``), CO 8 hour,
  SO2 and NO2 1 hour (daily maximum of the 1 hour values, SO2 uses the 24 hour
  average for the upper part of the scale).
* MEP: for the daily report, the daily average of SO2, NO2, CO, PM10 and PM2.5
  and the daily maximum of the 8 hour averages of ozone; for the real time
  report, the 1 hour averages (``*_1h``).

The library does not compute averages, apart from the PM :ref:`NowCast
<nowcast>`. Rolling or fixed windows are up to the caller.

.. _nowcast:

NowCast
-------

The EPA reports the current air quality from hourly PM2.5 and PM10 readings
with the NowCast, an average of the last 12 hours that follows quick changes
(TAD, "How the NowCast is calculated"):

#. the weight factor is ``1 - (max - min) / max`` of the 12 readings, and at
   least 0.5 (which approximates an average of the last 3 hours),
#. each reading is weighted by the factor raised to the number of hours ago
   (0 for the current hour),
#. the NowCast is the sum of the weighted readings over the sum of the weights.

When the air quality is stable the factor is close to 1 and the NowCast is
close to the plain 12 hour average, when it changes quickly the recent hours
weigh more. 2 of the last 3 hours must be valid.

The NowCast is only an aggregation of concentrations, the index comes from an
algorithm as usual, so it works with any algorithm (``algo='mep'`` too). It
is defined for PM only: ozone has its own method (a rolling two weeks window,
not implemented) and SO2 and NO2 are 1 hour averages already.

* :func:`aqi.to_nowcast` returns the NowCast concentration, to be converted with
  :func:`aqi.to_iaqi`,
* :func:`aqi.to_nowcast_aqi` goes all the way to the AQI from the readings of
  PM2.5 and PM10.

Readings are strings, oldest first, the last one is the current hour and
``None`` is a missing hour. Two parameters go beyond the standard, both keep
its formula:

* ``hours=`` is the window, 12 in the standard (at least 3),
* ``min_weight=`` is the lower limit of the weight factor, ``'0.5'`` in the
  standard, between ``'0'`` (only the current hour counts) and ``'1'`` (plain
  average). A lower limit follows the changes more closely.

Why a shorter window: air quality can change within the hour, for example when
a strong wind clears the smoke or when a fire plume arrives, and a 12 hour
weighted average hides it for hours. The World Air Quality Index project
discusses this in `A Beginner's Guide to Air Quality Instant-Cast and Now-Cast
<https://aqicn.org/faq/2015-03-15/air-quality-nowcast-a-beginners-guide/be/>`_
(2015, edited 2020) and proposes, for Asian conditions, a 3 hour window with a
lower limit of 1/10 on the weight factor instead of the 1/2 of the EPA. That is
``hours=3, min_weight='0.1'``. With ``hours=3`` alone the limit stays at 0.5,
which is less reactive: for the readings 10, 20 and 60 the current hour holds
57% of the weight with 0.5 and 84% with 0.1.

::

    import aqi
    pm25 = ['9.0', '12.1', '14.3', '20.5', '35.0', '41.2', None, '55.0']
    aqi.to_nowcast(aqi.POLLUTANT_PM25, pm25)              # NowCast concentration
    aqi.to_nowcast_aqi([(aqi.POLLUTANT_PM25, pm25)])      # AQI
    aqi.to_nowcast_aqi([(aqi.POLLUTANT_PM25, pm25)], hours=3, min_weight='0.1',
                       algo='mep')

Which pollutants
----------------

``to_aqi`` returns the highest IAQI of what it is given. The standards say
which pollutants an agency has to report and when a pollutant may be left out,
python-aqi does not enforce it: give it every pollutant you measured. A pollutant
that the algorithm does not know is ignored.

Categories and colours
----------------------

The library returns numbers, not categories. The standards map index values to
a category and a colour:

.. list-table::
   :header-rows: 1

   * - Index
     - EPA
     - Index
     - MEP (HJ 633-2026)
   * - 0 – 50
     - Good, green
     - 1 – 50
     - 优 (excellent), green
   * - 51 – 100
     - Moderate, yellow
     - 51 – 100
     - 良 (good), yellow
   * - 101 – 150
     - Unhealthy for Sensitive Groups, orange
     - 101 – 150
     - 轻度污染 (lightly polluted), orange
   * - 151 – 200
     - Unhealthy, red
     - 151 – 200
     - 中度污染 (moderately polluted), red
   * - 201 – 300
     - Very Unhealthy, purple
     - 201 – 300
     - 重度污染 (heavily polluted), purple
   * - 301 – 500
     - Hazardous, maroon
     - above 300
     - 严重污染 (severely polluted), maroon

Several sensors or monitors
---------------------------

The functions take one value per pollutant. For the EPA, the TAD says to take
the highest concentration among all the monitors of the reporting area.
Averaging two or three cheap sensors is not described by any standard, it is a
choice for the calling code: average them (or not) before calling the library.
