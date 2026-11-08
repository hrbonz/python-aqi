import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from decimal import ROUND_HALF_EVEN, Decimal
from unittest import mock

import aqi
from aqi.algos.epa import AQI as EPA
from aqi.algos.mep import AQI as MEP
from aqi.exceptions import OutOfRangeError


def top_of_scale(algo, elem):
    """Return the highest breakpoint concentration and the precision step"""
    pw = algo.piecewise
    return pw["bp"][elem][-1][1], pw["prec"][elem]


class TestOutOfRangeError(unittest.TestCase):
    def test_is_a_value_error(self):
        self.assertTrue(issubclass(OutOfRangeError, ValueError))

    def test_exported(self):
        self.assertIs(aqi.OutOfRangeError, OutOfRangeError)

    def test_attributes(self):
        err = OutOfRangeError("pm25", Decimal("600"), Decimal("0"), Decimal("500.4"))
        self.assertEqual(err.elem, "pm25")
        self.assertEqual(err.value, Decimal("600"))
        self.assertEqual(err.low, Decimal("0"))
        self.assertEqual(err.high, Decimal("500.4"))
        self.assertIn("pm25", str(err))
        self.assertIn("600", str(err))


class TestIaqiOutOfRange(unittest.TestCase):
    """The default behaviour is to raise, never to cap or crash"""

    def test_top_of_scale_is_valid(self):
        for algo in (EPA(), MEP()):
            for elem in algo.piecewise["bp"]:
                with self.subTest(algo=type(algo).__module__, elem=elem):
                    top, _ = top_of_scale(algo, elem)
                    algo.iaqi(elem, str(top))

    def test_above_top_raises(self):
        for algo in (EPA(), MEP()):
            for elem in algo.piecewise["bp"]:
                with self.subTest(algo=type(algo).__module__, elem=elem):
                    top, step = top_of_scale(algo, elem)
                    with self.assertRaises(OutOfRangeError) as ctx:
                        algo.iaqi(elem, str(top + step))
                    self.assertEqual(ctx.exception.elem, elem)
                    self.assertEqual(ctx.exception.value, top + step)
                    self.assertEqual(ctx.exception.high, top)

    def test_negative_raises(self):
        for algo in (EPA(), MEP()):
            for elem in algo.piecewise["bp"]:
                # a negative value must not be truncated to zero
                for value in ("-1", "-0.0001"):
                    with self.subTest(algo=type(algo).__module__, elem=elem, v=value):
                        with self.assertRaises(OutOfRangeError):
                            algo.iaqi(elem, value)

    def test_never_index_error(self):
        with self.assertRaises(ValueError):
            aqi.to_iaqi(aqi.POLLUTANT_PM25, "99999")

    def test_to_aqi_raises(self):
        with self.assertRaises(OutOfRangeError):
            aqi.to_aqi([(aqi.POLLUTANT_PM25, "12"), (aqi.POLLUTANT_PM10, "9999")])


class TestIaqiExtrapolate(unittest.TestCase):
    """EPA: AQI above 500 is "Beyond the AQI", computed with the last band"""

    def expected(self, elem, cc):
        pw = EPA.piecewise
        bplo, bphi = pw["bp"][elem][-1]
        aqilo, aqihi = pw["aqi"][-1]
        value = (aqihi - aqilo) / (bphi - bplo) * (Decimal(cc) - bplo) + aqilo
        return value.quantize(Decimal("1."), rounding=ROUND_HALF_EVEN)

    def test_epa_extrapolates_on_request(self):
        for elem in (aqi.POLLUTANT_PM25, aqi.POLLUTANT_PM10, aqi.POLLUTANT_CO_8H):
            with self.subTest(elem=elem):
                top, _ = top_of_scale(EPA(), elem)
                cc = top * 2
                value = EPA().iaqi(elem, str(cc), extrapolate=True)
                self.assertGreater(value, 500)
                self.assertEqual(value, self.expected(elem, cc))

    def test_in_range_unchanged_by_flag(self):
        self.assertEqual(
            EPA().iaqi(aqi.POLLUTANT_PM25, "35.9", extrapolate=True),
            EPA().iaqi(aqi.POLLUTANT_PM25, "35.9"),
        )

    def test_epa_pollutants_without_full_scale_still_raise(self):
        # 8h ozone stops at AQI 300, the standard uses 1h ozone above that
        top, step = top_of_scale(EPA(), aqi.POLLUTANT_O3_8H)
        with self.assertRaises(OutOfRangeError):
            EPA().iaqi(aqi.POLLUTANT_O3_8H, str(top + step), extrapolate=True)

    def test_mep_never_extrapolates(self):
        for elem in MEP.piecewise["bp"]:
            with self.subTest(elem=elem):
                top, step = top_of_scale(MEP(), elem)
                with self.assertRaises(OutOfRangeError):
                    MEP().iaqi(elem, str(top + step), extrapolate=True)

    def test_negative_still_raises(self):
        with self.assertRaises(OutOfRangeError):
            EPA().iaqi(aqi.POLLUTANT_PM25, "-1", extrapolate=True)

    def test_to_iaqi_and_to_aqi(self):
        self.assertGreater(
            aqi.to_iaqi(aqi.POLLUTANT_PM25, "800", extrapolate=True), 500
        )
        self.assertGreater(
            aqi.to_aqi(
                [(aqi.POLLUTANT_PM25, "800"), (aqi.POLLUTANT_PM10, "50")],
                extrapolate=True,
            ),
            500,
        )


class TestCcOutOfRange(unittest.TestCase):
    def test_above_500_raises(self):
        with self.assertRaises(OutOfRangeError):
            EPA().cc(aqi.POLLUTANT_PM25, "501")

    def test_negative_raises(self):
        with self.assertRaises(OutOfRangeError):
            EPA().cc(aqi.POLLUTANT_PM25, "-1")

    def test_iaqi_beyond_pollutant_scale_raises(self):
        # 8h ozone only has bands up to AQI 300, this used to be an IndexError
        with self.assertRaises(OutOfRangeError):
            EPA().cc(aqi.POLLUTANT_O3_8H, "301")

    def test_extrapolate_round_trip(self):
        top, _ = top_of_scale(EPA(), aqi.POLLUTANT_PM25)
        cc = EPA().cc(aqi.POLLUTANT_PM25, "600", extrapolate=True)
        self.assertGreater(cc, top)
        self.assertEqual(EPA().iaqi(aqi.POLLUTANT_PM25, str(cc), extrapolate=True), 600)

    def test_mep_does_not_extrapolate(self):
        with self.assertRaises(OutOfRangeError):
            MEP().cc(aqi.POLLUTANT_PM25, "501", extrapolate=True)

    def test_to_cc(self):
        with self.assertRaises(OutOfRangeError):
            aqi.to_cc(aqi.POLLUTANT_PM25, "600")
        top, _ = top_of_scale(EPA(), aqi.POLLUTANT_PM25)
        self.assertGreater(aqi.to_cc(aqi.POLLUTANT_PM25, "600", extrapolate=True), top)


class TestConsole(unittest.TestCase):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "argv", ["aqi", *args]):
            with redirect_stdout(out), redirect_stderr(err):
                with self.assertRaises(SystemExit) as ctx:
                    aqi.console_aqi()
        return ctx.exception.code, out.getvalue(), err.getvalue()

    def test_in_range(self):
        code, out, _ = self.run_cli("epa:2012", "pm25:12.1")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "51")

    def test_out_of_range_fails_cleanly(self):
        code, out, err = self.run_cli("aqi.algos.epa", "pm25:800")
        self.assertEqual(code, 3)
        self.assertEqual(out, "")
        self.assertIn("pm25", err)
        self.assertNotIn("Traceback", err)

    def test_extrapolate_flag(self):
        code, out, _ = self.run_cli("-e", "aqi.algos.epa", "pm25:800")
        self.assertEqual(code, 0)
        self.assertGreater(int(out.strip()), 500)

    def test_cc_out_of_range(self):
        code, _, err = self.run_cli("-c", "cc", "aqi.algos.epa", "pm25:600")
        self.assertEqual(code, 3)
        self.assertNotIn("Traceback", err)
