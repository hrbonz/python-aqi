from decimal import ROUND_DOWN, ROUND_HALF_EVEN, Decimal

from aqi.exceptions import NotApplicableError, OutOfRangeError


def derive_piecewise(parent, bp=None, prec=None, units=None, aqi=None):
    """Build the ``piecewise`` table of a new version of a standard from the
    previous one, only the given parts are replaced.

    :param parent: the ``piecewise`` dict of the previous version
    :param bp: breakpoints by pollutant to replace or add
    :param prec: precisions by pollutant to replace or add
    :param units: units by pollutant to replace or add
    :param aqi: new list of AQI bands, replaces the whole list
    :return: a new dict, ``parent`` is left untouched
    """
    return {
        "aqi": list(parent["aqi"] if aqi is None else aqi),
        "bp": {**parent["bp"], **(bp or {})},
        "prec": {**parent["prec"], **(prec or {})},
        "units": {**parent["units"], **(units or {})},
    }


class BaseAQI:
    """A generic AQI class"""

    def iaqi(self, elem, cc, extrapolate=False):
        """Calculate an intermediate AQI for a given pollutant. This is
        the heart of the algo. Return the IAQI for the given pollutant.

        .. warning:: the concentration is passed as a string so
        :class:`decimal.Decimal` doesn't act up with binary floats.

        :param elem: pollutant constant
        :type elem: int
        :param cc: pollutant concentration (µg/m³ or ppm)
        :type cc: str
        :param extrapolate: compute values beyond the scale if the standard
                            allows it, otherwise raise
        :type extrapolate: bool
        :raises OutOfRangeError: the concentration is not covered
        """
        raise NotImplementedError

    def aqi(self, ccs, iaqis=False, extrapolate=False):
        """Calculate the AQI based on a list of pollutants. Return an
        AQI value, if `iaqis` is set to True, send back a tuple
        containing the AQI and a dict of IAQIs.

        :param ccs: a list of tuples of pollutants concentrations with
                    pollutant constant and concentration as values
        :type ccs: list
        :param iaqis: return IAQIs with result
        :type iaqis: bool
        :param extrapolate: see :meth:`iaqi`
        :type extrapolate: bool
        """
        _iaqis = {}
        skipped = None
        for elem, cc in ccs:
            try:
                _iaqi = self.iaqi(elem, cc, extrapolate=extrapolate)
            except NotApplicableError as err:
                # blank in the table: the standard says to disregard the value
                skipped = err
                continue
            if _iaqi is not None:
                _iaqis[elem] = _iaqi
        if not _iaqis and skipped is not None:
            raise skipped
        _aqi = max(_iaqis.values())
        if iaqis:
            return (_aqi, _iaqis)
        else:
            return _aqi

    def cc(self, elem, iaqi, extrapolate=False):
        """Calculate a concentration for a given pollutant. Return the
        concentration for the given pollutant based on the intermediate AQI.

        .. warning:: the intermediate AQI is passed as a string

        :param elem: pollutant constant
        :type elem: int
        :param cc: intermediate AQI
        :type cc: str
        :param extrapolate: see :meth:`iaqi`
        :type extrapolate: bool
        :raises OutOfRangeError: the AQI value is not covered
        """
        raise NotImplementedError

    def list_pollutants(self):
        """List pollutants covered by an algorithm, return a list of
        pollutant names.
        """
        raise NotImplementedError


class PiecewiseAQI(BaseAQI):
    """A piecewise function AQI class (like EPA or MEP)

    A pollutant's breakpoints are a list with one ``(low, high)`` tuple per AQI
    band, ``None`` for a band the standard leaves blank. Values outside of the
    breakpoints raise :class:`OutOfRangeError` (:class:`NotApplicableError`
    for a blank band). An
    algorithm whose standard describes how to go beyond the top of the scale
    sets ``extrapolation`` to True: a pollutant whose table covers the whole
    scale then extends its last band when ``extrapolate`` is requested.
    """

    piecewise = None
    extrapolation = False

    def _check(self, elem):
        if self.piecewise is None:
            raise NameError("piecewise struct is not defined")
        return elem in self.piecewise["bp"]

    def _can_extrapolate(self, elem):
        """Only pollutants with a band for every AQI band can extend the top"""
        return self.extrapolation and len(self.piecewise["bp"][elem]) == len(
            self.piecewise["aqi"]
        )

    def iaqi(self, elem, cc, extrapolate=False):
        if not self._check(elem):
            return None

        raw = Decimal(cc)
        _cc = raw.quantize(self.piecewise["prec"][elem], rounding=ROUND_DOWN)

        # define breakpoints for this pollutant at this concentration
        bps = self.piecewise["bp"][elem]
        filled = [bp for bp in bps if bp is not None]
        low, high = filled[0][0], filled[-1][1]
        # a negative value must not be truncated to zero
        if raw < 0:
            raise OutOfRangeError(elem, raw, low, high)

        idx = None
        for i, bp in enumerate(bps):
            if bp is not None and bp[0] <= _cc <= bp[1]:
                idx = i
                break
        if idx is None:
            if _cc > high and extrapolate and self._can_extrapolate(elem):
                idx = len(bps) - 1
            elif _cc < low and bps[0] is None:
                raise NotApplicableError(elem, _cc, low, high)
            else:
                raise OutOfRangeError(elem, _cc, low, high)
        bplo, bphi = bps[idx]
        # get corresponding AQI boundaries
        (aqilo, aqihi) = self.piecewise["aqi"][idx]

        # equation
        value = (aqihi - aqilo) / (bphi - bplo) * (_cc - bplo) + aqilo
        return value.quantize(Decimal("1."), rounding=ROUND_HALF_EVEN)

    def cc(self, elem, iaqi, extrapolate=False):
        if not self._check(elem):
            return None

        _iaqi = int(iaqi)

        # define aqi breakpoints for this pollutant at this IAQI
        bps = self.piecewise["aqi"]
        ccs = self.piecewise["bp"][elem]
        low, high = bps[0][0], bps[-1][1]
        if _iaqi < low:
            raise OutOfRangeError(elem, _iaqi, low, high)

        idx = None
        for i, bp in enumerate(bps):
            if bp[0] <= _iaqi <= bp[1]:
                idx = i
                break
        if idx is None:
            if extrapolate and self._can_extrapolate(elem):
                idx = len(bps) - 1
            else:
                raise OutOfRangeError(elem, _iaqi, low, high)
        elif idx >= len(ccs):
            # this pollutant has no band for this part of the scale
            raise OutOfRangeError(elem, _iaqi, low, bps[len(ccs) - 1][1])
        elif ccs[idx] is None:
            first = next(i for i, bp in enumerate(ccs) if bp is not None)
            raise NotApplicableError(elem, _iaqi, bps[first][0], bps[-1][1])
        bplo, bphi = bps[idx]
        # get corresponding concentration boundaries
        (cclo, cchi) = ccs[idx]

        # equation
        value = (cchi - cclo) / (bphi - bplo) * (_iaqi - bplo) + cclo
        return Decimal(value).quantize(
            self.piecewise["prec"][elem], rounding=ROUND_DOWN
        )

    def list_pollutants(self):
        return self.piecewise["units"].items()
