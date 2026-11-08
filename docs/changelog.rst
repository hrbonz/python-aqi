Changelog
=========

1.0.0 (unreleased)
------------------

Standards
~~~~~~~~~

* New ``epa:2015`` (2015 ozone standard) and ``epa:2024`` (2024 PM2.5
  standard, single Hazardous category) tables, ``epa:2012`` being the tables of
  0.6.
* New ``mep:2026`` for the Chinese standard HJ 633-2026 (effective
  2026-03-01): lower PM10 and PM2.5 limits for IAQI 100, IAQI and AQI rounded
  up, concentrations rounded to integers (CO to one decimal), SO2 1 hour and
  ozone 8 hour above 800 µg/m³ fixed to IAQI 200 and 300. ``mep:2012`` being
  the tables of 0.6.
* Old versions stay selectable: ``algo='epa:2012'``, ``'mep:2012'``, or the
  ``ALGO_*_<year>`` constants. ``aqi.available_algos()`` lists them, ``aqi -l``
  too, and the ``aqi`` command takes ``epa:2012`` as the algorithm.
* The PDFs of the standards are archived in the repository
  (:doc:`standards/index`) and the documentation describes each version
  (:doc:`versions`).
* Interactive charts and tables compare the versions of a standard
  (:doc:`compare`), built from the library when the documentation is built.

Breaking changes
~~~~~~~~~~~~~~~~

* The default algorithm (``ALGO_EPA``, ``'epa'``, ``aqi.algos.epa``, and the
  same for MEP) is the **latest** version: the same concentration can give a
  different index than in 0.6, see :ref:`upgrading <upgrading-from-0.6>`.
  ``epa:2012`` and ``mep:2012`` give the 0.6.1 results.
* Python 2 is not supported anymore, Python 3.9 or later is required.
* Values outside of the table of the standard raise
  :class:`aqi.OutOfRangeError` (a ``ValueError``) instead of an
  ``IndexError`` or a wrong number, negative values included. The CLI prints a
  message and exits with code 3. Nothing is capped.
* An unknown ``algo=`` raises ``ValueError``.

New
~~~

* ``extrapolate=True`` (``-e`` on the command line) computes the EPA values
  above 500 ("Beyond the AQI").
* ``aqi.NotApplicableError`` for a pollutant the table leaves blank at that
  concentration (1 hour ozone below 0.125 ppm), ignored by :func:`aqi.to_aqi`
  when other pollutants are given.
* All the pollutant constants are exported by ``aqi`` (``POLLUTANT_CO_1H``,
  ``POLLUTANT_CO_24H``, ``POLLUTANT_NO2_24H``, ``POLLUTANT_SO2_24H``).
* ``derive_piecewise`` to write the next version of a standard as the changes
  from the previous one.

Fixes
~~~~~

* ``aqi -l`` crashed on Python 3.
* 1 hour ozone: the first bands of the EPA table were ``(0, 0)`` (still the case
  in ``epa:2012`` for compatibility).
* IAQI and AQI of the Chinese standard are rounded up as HJ 633 says
  (``mep:2026``), CO has one decimal.
* "contentration" typo in the docstrings.

Project
~~~~~~~

* Packaging with hatch (``pyproject.toml``) and uv, ruff through pre-commit,
  GitHub Actions instead of Travis, tests in ``tests/``.
* Documentation: standards and versions, concepts, API reference, this
  changelog.

0.6.1 and before
----------------

See the `releases <https://github.com/hrbonz/python-aqi/tags>`_ on GitHub.
