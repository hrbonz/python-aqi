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

The library does not compute averages, and it does not implement the EPA
NowCast (issue 19) that the EPA uses to turn hourly PM readings into an index
close to real time. Rolling or fixed windows are up to the caller.

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
