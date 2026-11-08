"""MEP HJ 633-2026, checked against the table and the clauses of the standard.

The table is transcribed again from ``docs/standards/hj633-2026.pdf`` (table 3,
see ``docs/standards/hj633-2026-table.rst``), it is not read from the code.
"""

import unittest
from decimal import Decimal

import aqi
import aqi.algos
from aqi.algos.mep import MEP, MEP_2012, MEP_2026
from aqi.exceptions import NotApplicableError, OutOfRangeError

IAQIS = [0, 50, 100, 150, 200, 300, 400, 500]

# concentration limits for each IAQI, "-" for a blank cell
TABLE_3 = {
    aqi.POLLUTANT_SO2_24H: "0 50 150 475 800 1600 2100 2620",
    aqi.POLLUTANT_SO2_1H: "0 150 500 650 800 - - -",
    aqi.POLLUTANT_NO2_24H: "0 40 80 180 280 565 750 940",
    aqi.POLLUTANT_NO2_1H: "0 100 200 700 1200 2340 3090 3840",
    aqi.POLLUTANT_CO_24H: "0 2 4 14 24 36 48 60",
    aqi.POLLUTANT_CO_1H: "0 5 10 35 60 90 120 150",
    aqi.POLLUTANT_O3_8H: "0 100 160 215 265 800 - -",
    aqi.POLLUTANT_O3_1H: "0 160 200 300 400 800 1000 1200",
    aqi.POLLUTANT_PM10: "0 50 120 250 350 420 500 600",
    aqi.POLLUTANT_PM25: "0 35 60 115 150 250 350 500",
}


def points(spec):
    return [None if item == "-" else Decimal(item) for item in spec.split()]


class TestTable3(unittest.TestCase):
    def test_every_limit_gives_its_iaqi_and_back(self):
        algo = MEP_2026()
        self.assertEqual(set(algo.piecewise["bp"]), set(TABLE_3))
        for elem, spec in TABLE_3.items():
            for iaqi, limit in zip(IAQIS, points(spec)):
                if limit is None:
                    continue
                with self.subTest(elem=elem, iaqi=iaqi, limit=limit):
                    self.assertEqual(algo.iaqi(elem, str(limit)), iaqi)
                    self.assertEqual(algo.cc(elem, str(iaqi)), limit)

    def test_only_pm10_and_pm25_changed(self):
        """Compared with HJ 633-2012, the limits for IAQI 100 of PM10 and PM2.5"""
        old = {
            elem: [bp[1] for bp in bps]
            for elem, bps in MEP_2012.piecewise["bp"].items()
        }
        for elem, spec in TABLE_3.items():
            new = [p for p in points(spec)[1:] if p is not None]
            with self.subTest(elem=elem):
                if elem == aqi.POLLUTANT_PM10:
                    self.assertEqual(old[elem][1], 150)
                    self.assertEqual(new[1], 120)
                    new[1] = old[elem][1]
                if elem == aqi.POLLUTANT_PM25:
                    self.assertEqual(old[elem][1], 75)
                    self.assertEqual(new[1], 60)
                    new[1] = old[elem][1]
                self.assertEqual(new, old[elem])

    def test_new_pm_limits(self):
        self.assertEqual(MEP_2012().iaqi("pm25", "60"), 82)  # 81.25 rounded up
        self.assertEqual(MEP_2026().iaqi("pm25", "60"), 100)
        self.assertEqual(MEP_2012().iaqi("pm10", "120"), 85)
        self.assertEqual(MEP_2026().iaqi("pm10", "120"), 100)

    def test_no_gap_between_limits(self):
        """The formula interpolates between neighbouring limits of the table"""
        algo = MEP_2026()
        # 35 is IAQI 50 and 36 is on the line to 60 (50 + 50 / 25), no jump
        self.assertEqual(algo.iaqi("pm25", "35"), 50)
        self.assertEqual(algo.iaqi("pm25", "36"), 52)
        self.assertEqual(algo.iaqi("pm25", "37"), 54)


class TestRounding(unittest.TestCase):
    """Clause 4.2.6: IAQI and AQI are rounded up, never down"""

    def test_results_are_rounded_up(self):
        algo = MEP_2026()
        # 50 + 50 / 70 * 10 = 57.14
        self.assertEqual(algo.iaqi("pm10", "60"), 58)
        # 50 + 50 / 40 * 10 = 62.5 (half-even would give 62)
        self.assertEqual(algo.iaqi("no2_24h", "50"), 63)

    def test_exact_values_are_not_pushed_up(self):
        algo = MEP_2026()
        for elem, spec in TABLE_3.items():
            for iaqi, limit in zip(IAQIS, points(spec)):
                if limit is not None:
                    with self.subTest(elem=elem, limit=limit):
                        self.assertEqual(algo.iaqi(elem, str(limit)), iaqi)
        # 50 + 50 / 25 * 10 is exactly 70
        self.assertEqual(algo.iaqi("pm25", "45"), 70)

    def test_aqi_is_the_highest_iaqi(self):
        self.assertEqual(
            MEP_2026().aqi([("pm25", "45"), ("pm10", "60"), ("no2_24h", "50")]), 70
        )

    def test_concentrations_are_rounded_to_integers(self):
        """GB/T 8170: the nearest, an exact 5 goes to the even digit"""
        algo = MEP_2026()
        self.assertEqual(algo.iaqi("pm25", "34.6"), 50)  # 35
        self.assertEqual(algo.iaqi("pm25", "35.4"), 50)  # 35
        self.assertEqual(algo.iaqi("pm25", "35.6"), 52)  # 36
        self.assertEqual(algo.iaqi("pm25", "36.5"), 52)  # 36
        self.assertEqual(algo.iaqi("pm25", "37.5"), 56)  # 38

    def test_co_is_rounded_to_one_decimal(self):
        """Issue 4: CO keeps one decimal"""
        algo = MEP_2026()
        self.assertEqual(algo.iaqi("co_24h", "2.04"), 50)  # 2.0
        self.assertEqual(algo.iaqi("co_24h", "2.06"), 53)  # 2.1: 50 + 25 * 0.1
        self.assertEqual(algo.iaqi("co_1h", "5.1"), 51)  # 50 + 10 * 0.1
        self.assertEqual(algo.cc("co_24h", "51"), Decimal("2.0"))
        self.assertEqual(algo.cc("co_24h", "100"), Decimal("4.0"))
        self.assertEqual(algo.piecewise["prec"]["co_24h"], Decimal("0.1"))
        self.assertEqual(algo.piecewise["prec"]["co_1h"], Decimal("0.1"))


class TestBeyondTheTable(unittest.TestCase):
    """Footnotes b and c of table 3 fix the IAQI above the table"""

    def test_so2_1h_above_800_is_200(self):
        for value in ("801", "1500", "9999"):
            self.assertEqual(MEP_2026().iaqi("so2_1h", value), 200)

    def test_o3_8h_above_800_is_300(self):
        for value in ("801", "1500", "9999"):
            self.assertEqual(MEP_2026().iaqi("o3_8h", value), 300)

    def test_in_a_list_of_pollutants(self):
        ccs = [("so2_1h", "900"), ("pm25", "10")]
        self.assertEqual(
            MEP_2026().aqi(ccs, iaqis=True), (200, {"so2_1h": 200, "pm25": 15})
        )

    def test_cc_does_not_go_back_there(self):
        with self.assertRaises(OutOfRangeError):
            MEP_2026().cc("so2_1h", "300")
        with self.assertRaises(OutOfRangeError):
            MEP_2026().cc("o3_8h", "400")

    def test_other_pollutants_still_raise(self):
        for elem, spec in TABLE_3.items():
            if elem in ("so2_1h", "o3_8h"):
                continue
            top = points(spec)[-1]
            with self.subTest(elem=elem):
                with self.assertRaises(OutOfRangeError):
                    MEP_2026().iaqi(elem, str(top + 1))
                with self.assertRaises(OutOfRangeError):
                    MEP_2026().iaqi(elem, str(top + 1), extrapolate=True)

    def test_negative_still_raises(self):
        with self.assertRaises(OutOfRangeError):
            MEP_2026().iaqi("so2_1h", "-1")

    def test_2012_does_not_compute_them(self):
        """HJ 633-2012 says they are not computed"""
        for elem in ("so2_1h", "o3_8h"):
            with self.subTest(elem=elem):
                with self.assertRaises(NotApplicableError):
                    MEP_2012().iaqi(elem, "801")

    def test_2012_aqi_uses_the_other_pollutants(self):
        """The 24 hour SO2 and the 1 hour O3 report instead"""
        ccs = [("so2_1h", "900"), ("so2_24h", "100")]
        self.assertEqual(MEP_2012().aqi(ccs, iaqis=True), (75, {"so2_24h": 75}))
        with self.assertRaises(NotApplicableError):
            MEP_2012().aqi([("o3_8h", "900")])


class TestMep2012(unittest.TestCase):
    """HJ 633-2012 as written: limit to limit, no rounding of concentrations,
    IAQI rounded up (clause 6.2)"""

    LIMITS = {
        "so2_24h": "0 50 150 475 800 1600 2100 2620",
        "pm10": "0 50 150 250 350 420 500 600",
        "pm25": "0 35 75 115 150 250 350 500",
        "co_24h": "0 2 4 14 24 36 48 60",
        "o3_8h": "0 100 160 215 265 800",
    }

    def test_limits_of_table_1(self):
        algo = MEP_2012()
        for elem, spec in self.LIMITS.items():
            for iaqi, limit in zip(IAQIS, spec.split()):
                with self.subTest(elem=elem, iaqi=iaqi):
                    self.assertEqual(algo.iaqi(elem, limit), iaqi)
                    self.assertEqual(algo.cc(elem, str(iaqi)), Decimal(limit))

    def test_no_gap_and_no_truncation(self):
        algo = MEP_2012()
        self.assertEqual(algo.iaqi("pm25", "35.5"), 51)  # 50 + 50 / 40 * 0.5
        self.assertEqual(algo.iaqi("pm25", "35.1"), 51)  # 50.125 rounded up
        self.assertEqual(algo.iaqi("co_24h", "2.1"), 53)  # 52.5 rounded up
        self.assertEqual(algo.iaqi("pm10", "50.4"), 51)

    def test_rounded_up(self):
        algo = MEP_2012()
        self.assertEqual(algo.iaqi("pm25", "60"), 82)  # 81.25
        self.assertEqual(algo.iaqi("pm10", "60"), 55)  # 55 exactly, not 56
        self.assertEqual(algo.iaqi("pm25", "0.1"), 1)

    def test_cc_round_trip(self):
        algo = MEP_2012()
        for elem in self.LIMITS:
            for iaqi in range(1, 301):
                with self.subTest(elem=elem, iaqi=iaqi):
                    cc = algo.cc(elem, str(iaqi))
                    self.assertEqual(algo.iaqi(elem, str(cc)), iaqi)

    def test_out_of_range(self):
        with self.assertRaises(OutOfRangeError):
            MEP_2012().iaqi("pm25", "500.1")
        with self.assertRaises(OutOfRangeError):
            MEP_2012().iaqi("pm25", "-0.1")


class TestSelection(unittest.TestCase):
    def test_versions(self):
        self.assertEqual(list(aqi.algos.mep.VERSIONS), ["2012", "2026"])
        self.assertIs(MEP, MEP_2026)
        self.assertIs(aqi.algos.mep.AQI, MEP_2026)

    def test_names_and_constants(self):
        self.assertEqual(aqi.ALGO_MEP_2026, "mep:2026")
        self.assertIn("mep:2026", aqi.available_algos())
        self.assertIsInstance(aqi.algos.get_algo("mep:2026"), MEP_2026)

    def test_default_is_the_latest(self):
        self.assertIsInstance(aqi.algos.get_algo(aqi.ALGO_MEP), MEP_2026)
        self.assertIsInstance(aqi.algos.get_algo("mep"), MEP_2026)
        self.assertEqual(aqi.to_iaqi("pm25", "60", algo=aqi.ALGO_MEP), 100)
        self.assertEqual(aqi.to_iaqi("pm25", "60", algo=aqi.ALGO_MEP_2012), 82)

    def test_docstring_cites_its_source(self):
        self.assertIn("HJ 633-2026", MEP_2026.__doc__)
        self.assertIn("table 3", MEP_2026.__doc__)
