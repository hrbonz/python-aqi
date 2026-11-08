API reference
=============

Functions
---------

.. automodule:: aqi
   :members: to_iaqi, to_aqi, to_cc, to_nowcast, to_nowcast_aqi,
             available_algos, get_algo, list_algos, console_aqi

Errors
------

.. autoexception:: aqi.OutOfRangeError

.. autoexception:: aqi.NotApplicableError

.. autoexception:: aqi.InsufficientDataError

Algorithms
----------

.. automodule:: aqi.algos
   :members: available_algos, get_algo, list_algos

.. automodule:: aqi.algos.base
   :members: BaseAQI, PiecewiseAQI, derive_piecewise

.. automodule:: aqi.algos.epa
   :members: EPA_2012, EPA_2015, EPA_2024, EPA

.. automodule:: aqi.algos.mep
   :members: MEP_2012, MEP_2026, MEP
