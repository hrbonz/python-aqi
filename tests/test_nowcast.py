import unittest
from decimal import Decimal
from fractions import Fraction

import aqi
from aqi.nowcast import nowcast


def reference(values, hours, floor=0.5):
    """The TAD steps written out with floats, ``values`` oldest first"""
    window = values[-hours:]
    high, low = max(window), min(window)
    weight = max(1 - (high - low) / high, floor) if high else 1
    ago = range(len(window) - 1, -1, -1)
    total = sum(v * weight**i for v, i in zip(window, ago))
    return total / sum(weight**i for i in ago)


class TestNowcast(unittest.TestCase):
    def test_stable_air_is_the_plain_average(self):
        self.assertEqual(nowcast("pm25", ["10"] * 12), 10)
        self.assertEqual(nowcast("pm10", ["12.1"] * 12), Decimal("12.1"))
        self.assertEqual(nowcast("pm25", ["0"] * 12), 0)

    def test_result_is_a_decimal(self):
        self.assertIsInstance(nowcast("pm25", ["10"] * 12), Decimal)

    def test_weight_factor_in_range(self):
        values = [8] * 11 + [10]  # weight factor 1 - 2 / 10 = 0.8
        got = nowcast("pm25", [str(v) for v in values])
        self.assertAlmostEqual(float(got), reference(values, 12), places=9)

    def test_varying_series(self):
        values = [35, 20, 12, 40, 55, 61, 80, 74, 66, 58, 90, 120]
        got = nowcast("pm25", [str(v) for v in values])
        self.assertAlmostEqual(float(got), reference(values, 12), places=9)

    def test_weight_factor_is_at_least_half(self):
        # 100 right now after 11 clean hours: the factor would be 0, it is 0.5
        got = nowcast("pm25", ["0"] * 11 + ["100"])
        self.assertEqual(
            Fraction(got).limit_denominator(10**6), Fraction(100 * 2048, 4095)
        )

    def test_the_last_hour_weighs_the_most(self):
        up = nowcast("pm25", ["10"] * 11 + ["100"])
        down = nowcast("pm25", ["100"] + ["10"] * 11)
        self.assertGreater(up, down)

    def test_exact_decimals(self):
        """No float noise at the edge of a band"""
        self.assertEqual(aqi.to_nowcast_aqi([("pm25", ["9.0"] * 12)]), 50)
        self.assertEqual(aqi.to_nowcast_aqi([("pm25", ["9.1"] * 12)]), 51)


class TestWindow(unittest.TestCase):
    def test_three_hours(self):
        # factor 1 - 20 / 30 = 1/3, raised to 0.5: 30 + 20 / 2 + 10 / 4 over 1.75
        got = nowcast("pm25", ["10", "20", "30"], hours=3)
        self.assertEqual(Fraction(got).limit_denominator(10**6), Fraction(170, 7))

    def test_older_readings_are_ignored(self):
        self.assertEqual(nowcast("pm25", ["1000"] + ["10"] * 12), 10)
        self.assertEqual(nowcast("pm25", ["1000", "10", "10", "10"], hours=3), 10)

    def test_short_list_is_missing_hours(self):
        self.assertEqual(
            nowcast("pm25", ["10", "20", "30"]),
            nowcast("pm25", ["10", "20", "30"], hours=3),
        )

    def test_other_windows(self):
        values = list(range(10, 34))
        for hours in (3, 6, 24):
            with self.subTest(hours=hours):
                got = nowcast("pm10", [str(v) for v in values], hours=hours)
                self.assertAlmostEqual(float(got), reference(values, hours), places=9)

    def test_window_is_at_least_3_hours(self):
        for hours in (2, 1, 0, -3, 3.0, "3", None, True):
            with self.subTest(hours=hours):
                with self.assertRaises(ValueError):
                    nowcast("pm25", ["10"] * 12, hours=hours)


class TestMinWeight(unittest.TestCase):
    """The lower limit of the weight factor, 0.5 in the standard"""

    def test_default_is_the_standard(self):
        series = ["10", "20", "60"]
        self.assertEqual(
            nowcast("pm25", series, hours=3),
            nowcast("pm25", series, hours=3, min_weight="0.5"),
        )
        got = nowcast("pm25", series, hours=3)
        self.assertEqual(Fraction(got).limit_denominator(10**6), Fraction(290, 7))

    def test_lower_limit_follows_the_changes_more_closely(self):
        # factor 0 for 100 after clean hours: 1, 0.1 and 0.01 are the weights
        got = nowcast("pm25", ["0", "0", "100"], hours=3, min_weight="0.1")
        self.assertEqual(Fraction(got).limit_denominator(10**6), Fraction(10000, 111))
        self.assertGreater(got, nowcast("pm25", ["0", "0", "100"], hours=3))

    def test_limit_is_only_a_floor(self):
        # the factor is 1/6 here, above 0.1: the limit does not matter
        series = ["10", "20", "60"]
        self.assertEqual(
            nowcast("pm25", series, hours=3, min_weight="0.1"),
            nowcast("pm25", series, hours=3, min_weight="0"),
        )
        values = [10, 20, 60]
        got = nowcast("pm25", ["10", "20", "60"], hours=3, min_weight="0.1")
        self.assertAlmostEqual(float(got), reference(values, 3, 0.1), places=9)

    def test_limits(self):
        series = ["10", "20", "60"]
        self.assertEqual(nowcast("pm25", series, hours=3, min_weight="1"), 30)
        self.assertEqual(
            nowcast("pm25", ["0", "0", "100"], hours=3, min_weight="0"), 100
        )

    def test_other_types_of_numbers(self):
        series = ["0", "0", "100"]
        expected = nowcast("pm25", series, hours=3, min_weight="0.1")
        self.assertEqual(
            nowcast("pm25", series, hours=3, min_weight=Decimal("0.1")), expected
        )

    def test_must_be_between_0_and_1(self):
        for value in ("-0.1", "1.1", "2", "abc", "", "NaN", "Infinity", None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    nowcast("pm25", ["10"] * 12, min_weight=value)


class TestMissingData(unittest.TestCase):
    def test_a_missing_hour_is_left_out(self):
        self.assertEqual(nowcast("pm25", ["10"] * 11 + [None]), 10)
        self.assertEqual(nowcast("pm25", [None] * 10 + ["10", "20"]), Decimal(50) / 3)

    def test_two_of_the_last_three_are_needed(self):
        for last in (
            [None, None, "10"],
            ["10", None, None],
            [None, "10", None],
            [None, None, None],
        ):
            with self.subTest(last=last):
                with self.assertRaises(aqi.InsufficientDataError):
                    nowcast("pm25", ["10"] * 9 + last)

    def test_two_of_three_is_enough(self):
        for last in ([None, "10", "10"], ["10", None, "10"], ["10", "10", None]):
            with self.subTest(last=last):
                self.assertEqual(nowcast("pm25", ["10"] * 9 + last), 10)

    def test_nothing(self):
        with self.assertRaises(aqi.InsufficientDataError):
            nowcast("pm25", [])

    def test_is_a_value_error(self):
        self.assertTrue(issubclass(aqi.InsufficientDataError, ValueError))


class TestInput(unittest.TestCase):
    def test_pm_only(self):
        for elem in (
            aqi.POLLUTANT_O3_8H,
            aqi.POLLUTANT_O3_1H,
            aqi.POLLUTANT_SO2_1H,
            aqi.POLLUTANT_NO2_1H,
            aqi.POLLUTANT_CO_8H,
            "unknown",
        ):
            with self.subTest(elem=elem):
                with self.assertRaises(ValueError) as ctx:
                    nowcast(elem, ["10"] * 12)
                self.assertIn("pm25", str(ctx.exception))

    def test_both_pm(self):
        for elem in (aqi.POLLUTANT_PM25, aqi.POLLUTANT_PM10):
            self.assertEqual(nowcast(elem, ["10"] * 12), 10)

    def test_negative_reading(self):
        with self.assertRaises(aqi.OutOfRangeError):
            nowcast("pm25", ["10"] * 11 + ["-1"])

    def test_not_a_number(self):
        for value in ("abc", "", "NaN", "Infinity"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    nowcast("pm25", ["10"] * 11 + [value])

    def test_tuple_and_generator_are_fine(self):
        self.assertEqual(nowcast("pm25", ("10",) * 12), 10)
        self.assertEqual(nowcast("pm25", (v for v in ["10"] * 12)), 10)


class TestApi(unittest.TestCase):
    def test_exported(self):
        self.assertIn("to_nowcast", aqi.__all__)
        self.assertIn("to_nowcast_aqi", aqi.__all__)
        self.assertIn("InsufficientDataError", aqi.__all__)

    def test_to_nowcast(self):
        self.assertEqual(aqi.to_nowcast("pm25", ["10"] * 12), 10)
        got = aqi.to_nowcast("pm25", ["10", "20", "30"], hours=3)
        self.assertAlmostEqual(float(got), 170 / 7)

    def test_to_nowcast_aqi_defaults_to_the_latest_epa(self):
        series = [("pm25", ["12.1"] * 12)]
        self.assertEqual(aqi.to_nowcast_aqi(series), aqi.to_iaqi("pm25", "12.1"))

    def test_any_algorithm(self):
        series = [("pm25", ["12.1"] * 12)]
        self.assertEqual(aqi.to_nowcast_aqi(series, algo="epa:2012"), 51)
        self.assertEqual(aqi.to_nowcast_aqi(series, algo=aqi.ALGO_MEP), 18)
        series = [("pm25", ["35"] * 12)]
        self.assertEqual(aqi.to_nowcast_aqi(series, algo="mep:2026"), 50)

    def test_several_pollutants_and_iaqis(self):
        series = [("pm25", ["12.1"] * 12), ("pm10", ["100"] * 12)]
        value, iaqis = aqi.to_nowcast_aqi(series, iaqis=True)
        self.assertEqual(iaqis["pm25"], aqi.to_iaqi("pm25", "12.1"))
        self.assertEqual(iaqis["pm10"], aqi.to_iaqi("pm10", "100"))
        self.assertEqual(value, max(iaqis.values()))

    def test_window(self):
        readings = ["10", "20", "60"]
        three = aqi.to_nowcast_aqi([("pm25", readings)], hours=3)
        twelve = aqi.to_nowcast_aqi([("pm25", ["10"] * 9 + readings)])
        self.assertGreater(three, 0)
        self.assertNotEqual(three, twelve)

    def test_min_weight(self):
        series = [("pm25", ["0", "0", "100"])]
        standard = aqi.to_nowcast_aqi(series, hours=3)
        asia = aqi.to_nowcast_aqi(series, hours=3, min_weight="0.1")
        self.assertGreater(asia, standard)
        self.assertEqual(
            aqi.to_nowcast("pm25", series[0][1], hours=3, min_weight="0.1"),
            Decimal(10000) / 111,
        )

    def test_not_enough_data(self):
        with self.assertRaises(aqi.InsufficientDataError):
            aqi.to_nowcast_aqi([("pm25", ["10"] * 10 + [None, None])])

    def test_ozone_is_refused(self):
        with self.assertRaises(ValueError):
            aqi.to_nowcast_aqi([("o3_8h", ["0.05"] * 12)])

    def test_unknown_algorithm(self):
        with self.assertRaises(ValueError):
            aqi.to_nowcast_aqi([("pm25", ["10"] * 12)], algo="nope")
