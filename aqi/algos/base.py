# -*- coding: utf-8 -*-

from decimal import *


class BaseAQI(object):
    """A generic AQI class"""

    def iaqi(self, elem, cc):
        """Calculate an intermediate AQI for a given pollutant. This is
        the heart of the algo. Return the IAQI for the given pollutant.

        .. warning:: the concentration is passed as a string so
        :class:`decimal.Decimal` doesn't act up with binary floats.

        :param elem: pollutant constant
        :type elem: int
        :param cc: pollutant contentration (µg/m³ or ppm)
        :type cc: str
        """
        raise NotImplementedError

    def aqi(self, ccs, iaqis=False):
        """Calculate the AQI based on a list of pollutants. Return an
        AQI value, if `iaqis` is set to True, send back a tuple
        containing the AQI and a dict of IAQIs.

        :param ccs: a list of tuples of pollutants concentrations with
                    pollutant constant and concentration as values
        :type ccs: list
        :param iaqis: return IAQIs with result
        :type iaqis: bool
        """
        _iaqis = {}
        for (elem, cc) in ccs:
            _iaqi = self.iaqi(elem, cc)
            if _iaqi is not None:
                _iaqis[elem] = _iaqi
        _aqi = max(_iaqis.values())
        if iaqis:
            return (_aqi, _iaqis)
        else:
            return _aqi

    def cc(self, elem, iaqi):
        """Calculate a concentration for a given pollutant. Return the
        concentration for the given pollutant based on the intermediate AQI.

        .. warning:: the intermediate AQI is passed as a string

        :param elem: pollutant constant
        :type elem: int
        :param cc: intermediate AQI
        :type cc: str
        """
        raise NotImplementedError

    def list_pollutants(self):
        """List pollutants covered by an algorithm, return a list of
        pollutant names.
        """
        raise NotImplementedError


class PiecewiseAQI(BaseAQI):
    """A piecewise function AQI class (like EPA or MEP)"""

    piecewise = None

    def iaqi(self, elem, cc):
        if self.piecewise is None:
            raise NameError("piecewise struct is not defined")
        if elem not in self.piecewise['bp'].keys():
            return None

        _cc = Decimal(cc).quantize(self.piecewise['prec'][elem],
                                   rounding=ROUND_DOWN)

        # define breakpoints for this pollutant at this contentration
        bps = self.piecewise['bp'][elem]
        bplo = None
        bphi = None
        idx = 0
        for bp in bps:
            if _cc >= bp[0] and _cc <= bp[1]:
                bplo = bp[0]
                bphi = bp[1]
                break
            idx += 1
        # get corresponding AQI boundaries
        (aqilo, aqihi) = self.piecewise['aqi'][idx]

        # equation
        value = (aqihi - aqilo) / (bphi - bplo) * (_cc - bplo) + aqilo
        return value.quantize(Decimal('1.'), rounding=ROUND_HALF_EVEN)


    def cc(self, elem, iaqi):
        if self.piecewise is None:
            raise NameError("piecewise struct is not defined")
        if elem not in self.piecewise['bp'].keys():
            return None

        _iaqi = int(iaqi)

        # define aqi breakpoints for this pollutant at this IAQI
        bps = self.piecewise['aqi']
        bplo = None
        bphi = None
        idx = 0
        for bp in bps:
            if _iaqi >= bp[0] and _iaqi <= bp[1]:
                bplo = bp[0]
                bphi = bp[1]
                break
            idx += 1
        # get corresponding concentration boundaries
        (cclo, cchi) = self.piecewise['bp'][elem][idx]

        # equation
        value = (cchi - cclo) / (bphi - bplo) * (_iaqi - bplo) + cclo
        return Decimal(value).quantize(self.piecewise['prec'][elem],
                                   rounding=ROUND_DOWN)

    def list_pollutants(self):
        return self.piecewise['units'].items()
