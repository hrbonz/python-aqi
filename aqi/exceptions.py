class OutOfRangeError(ValueError):
    """A concentration or an AQI value is outside of what an algorithm covers.

    Standards define a scale (0 to 500 for the EPA AQI), values outside of it
    are not capped because that would hide how far off the scale they are.
    Code using the library decides what to do with them.

    :param elem: pollutant constant
    :param value: the value that was refused
    :param low: lowest value covered by the algorithm for this pollutant
    :param high: highest value covered by the algorithm for this pollutant
    """

    def __init__(self, elem, value, low, high):
        self.elem = elem
        self.value = value
        self.low = low
        self.high = high
        super().__init__(
            f"{elem}: {value} is not covered by the algorithm "
            f"(valid range is {low} to {high})"
        )


class NotApplicableError(OutOfRangeError):
    """The standard leaves this part of the scale blank for the pollutant.

    EPA 1 hour ozone has no value below 0.125 ppm (AQI 101): the standard says
    to disregard it and to use 8 hour ozone. :meth:`BaseAQI.aqi` does so, a
    direct call to ``iaqi`` or ``cc`` raises this error. HJ 633-2012 does the
    same above the table for SO2 1 hour and O3 8 hour.
    """
