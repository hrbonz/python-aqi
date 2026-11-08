"""The NowCast: an average of the last hourly PM readings that follows fast
changes, which the EPA uses to report the air quality close to real time.

The standard defines it for PM2.5 and PM10 only (ozone has a different
method), see the Technical Assistance Document, "How the NowCast is
calculated". It is an aggregation of concentrations, converting the result to
an index is the job of an algorithm (:func:`aqi.to_nowcast_aqi`).
"""

from decimal import Decimal, InvalidOperation
from fractions import Fraction

from aqi.constants import POLLUTANT_PM10, POLLUTANT_PM25
from aqi.exceptions import InsufficientDataError, OutOfRangeError

#: the pollutants that the standard defines a NowCast for
NOWCAST_POLLUTANTS = (POLLUTANT_PM25, POLLUTANT_PM10)
#: the window of the standard
DEFAULT_HOURS = 12
#: shortest window, 2 of the last 3 hours must be valid
MIN_HOURS = 3
#: the weight factor is never lower than this, it approximates a 3 hour average
DEFAULT_MIN_WEIGHT = "0.5"


def _reading(elem, value):
    """A reading as a ``Fraction``, ``None`` for a missing hour"""
    if value is None:
        return None
    try:
        number = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{elem}: {value!r} is not a concentration") from None
    if not number.is_finite():
        raise ValueError(f"{elem}: {value!r} is not a concentration")
    if number < 0:
        raise OutOfRangeError(elem, number, Decimal(0), Decimal("Infinity"))
    return Fraction(number)


def _min_weight(value):
    """The lower limit of the weight factor as a ``Fraction``, 0 to 1"""
    try:
        number = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"min_weight {value!r} is not a number") from None
    if not number.is_finite() or not 0 <= number <= 1:
        raise ValueError(f"min_weight must be between 0 and 1, not {value!r}")
    return Fraction(number)


def nowcast(elem, hourly, hours=DEFAULT_HOURS, min_weight=DEFAULT_MIN_WEIGHT):
    """Calculate the NowCast concentration of PM2.5 or PM10.

    The weight factor is ``1 - (max - min) / max`` of the readings of the
    window, at least ``min_weight`` (0.5). The NowCast is the average of the
    readings weighted by the factor raised to the number of hours ago (0 for
    the current hour): close to the plain average when the air quality is
    stable, close to an average of the last 3 hours when it changes quickly.

    .. warning:: the readings are passed as strings so :class:`decimal.Decimal`
        doesn't act up with binary floats.

    The result is not rounded, an algorithm truncates it to the precision of
    the pollutant when it converts it to an index.

    :param elem: pollutant constant, ``POLLUTANT_PM25`` or ``POLLUTANT_PM10``
    :type elem: str
    :param hourly: hourly concentrations (µg/m³), oldest first, the last one
                   is the current hour, ``None`` for a missing hour. A list
                   shorter than the window means the earlier hours are missing.
    :type hourly: list
    :param hours: length of the window, 12 in the standard. Other values (3 is
                  often used for fast changing episodes) are not part of the
                  standard. At least 3.
    :type hours: int
    :param min_weight: lower limit of the weight factor, between 0 and 1 (a
                       string, like the readings). 0.5 in the standard, a lower
                       value follows the changes more closely: 1 is the plain
                       average, 0 only counts the current hour. 0.1 with a
                       3 hour window is the proposal of aqicn.org for Asia.
    :type min_weight: str
    :return: the NowCast concentration
    :rtype: decimal.Decimal
    :raises ValueError: the pollutant has no NowCast, the window is shorter
                        than 3 hours, a reading is not a number or
                        ``min_weight`` is not between 0 and 1
    :raises OutOfRangeError: a reading is negative
    :raises InsufficientDataError: less than 2 of the last 3 hours are valid
    """
    if elem not in NOWCAST_POLLUTANTS:
        raise ValueError(
            f"{elem}: the NowCast is defined for "
            f"{' and '.join(NOWCAST_POLLUTANTS)} only (ozone has its own method, "
            "SO2 and NO2 are 1 hour averages already)"
        )
    if isinstance(hours, bool) or not isinstance(hours, int) or hours < MIN_HOURS:
        raise ValueError(f"the window is at least {MIN_HOURS} hours, not {hours!r}")

    floor = _min_weight(min_weight)
    window = [_reading(elem, value) for value in list(hourly)[-hours:]]
    # an earlier hour that was not given is a missing hour
    window = [None] * (hours - len(window)) + window

    if sum(value is not None for value in window[-3:]) < 2:
        raise InsufficientDataError(
            f"{elem}: 2 of the last 3 hours must be valid for a NowCast"
        )

    # number of hours ago -> reading
    valid = {
        hours - 1 - i: value for i, value in enumerate(window) if value is not None
    }
    high, low = max(valid.values()), min(valid.values())
    weight = max(1 - (high - low) / high, floor) if high else Fraction(1)

    total = sum(value * weight**ago for ago, value in valid.items())
    norm = sum(weight**ago for ago in valid)
    result = total / norm
    # exact when the result is a finite decimal, correctly rounded otherwise
    return Decimal(result.numerator) / Decimal(result.denominator)
