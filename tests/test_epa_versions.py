"""EPA 2015 and 2024 tables, checked against the Technical Assistance Documents.

The tables below are transcribed again from the PDFs in ``docs/standards/``
(the "Breakpoints for the AQI" table), they are not read from the code.
"""

import unittest
from decimal import Decimal

import aqi
import aqi.algos
from aqi.algos.epa import EPA, EPA_2012, EPA_2015, EPA_2024
from aqi.exceptions import NotApplicableError, OutOfRangeError


def bands(spec):
    """'0.0-12.0 12.1-35.4 -' -> [(Decimal, Decimal), (...), None]"""
    out = []
    for item in spec.split():
        if item == "-":
            out.append(None)
        else:
            lo, hi = item.split("-")
            out.append((Decimal(lo), Decimal(hi)))
    return out


AQI_7 = [(0, 50), (51, 100), (101, 150), (151, 200), (201, 300), (301, 400), (401, 500)]
AQI_6 = AQI_7[:5] + [(301, 500)]

# EPA-454/B-18-007 (September 2018), Table 5, the Hazardous category is
# split in two, the 2015 ozone standard is in
TAD_2018 = {
    aqi.POLLUTANT_O3_8H: "0.000-0.054 0.055-0.070 0.071-0.085 0.086-0.105 0.106-0.200",
    aqi.POLLUTANT_O3_1H: "- - 0.125-0.164 0.165-0.204 0.205-0.404 0.405-0.504 "
    "0.505-0.604",
    aqi.POLLUTANT_PM25: "0.0-12.0 12.1-35.4 35.5-55.4 55.5-150.4 150.5-250.4 "
    "250.5-350.4 350.5-500.4",
    aqi.POLLUTANT_PM10: "0-54 55-154 155-254 255-354 355-424 425-504 505-604",
    aqi.POLLUTANT_CO_8H: "0.0-4.4 4.5-9.4 9.5-12.4 12.5-15.4 15.5-30.4 30.5-40.4 "
    "40.5-50.4",
    aqi.POLLUTANT_SO2_1H: "0-35 36-75 76-185 186-304 305-604 605-804 805-1004",
    aqi.POLLUTANT_NO2_1H: "0-53 54-100 101-360 361-649 650-1249 1250-1649 1650-2049",
}

# EPA-454/B-24-002 (May 2024) and EPA-403/B-26-003 (May 2026), Table 6, one
# Hazardous category (301-500) whose top is the concentration for AQI 500
TAD_2024 = {
    aqi.POLLUTANT_O3_8H: TAD_2018[aqi.POLLUTANT_O3_8H],
    aqi.POLLUTANT_O3_1H: "- - 0.125-0.164 0.165-0.204 0.205-0.404 0.405-0.604",
    aqi.POLLUTANT_PM25: "0.0-9.0 9.1-35.4 35.5-55.4 55.5-125.4 125.5-225.4 225.5-325.4",
    aqi.POLLUTANT_PM10: "0-54 55-154 155-254 255-354 355-424 425-604",
    aqi.POLLUTANT_CO_8H: "0.0-4.4 4.5-9.4 9.5-12.4 12.5-15.4 15.5-30.4 30.5-50.4",
    aqi.POLLUTANT_SO2_1H: "0-35 36-75 76-185 186-304 305-604 605-1004",
    aqi.POLLUTANT_NO2_1H: "0-53 54-100 101-360 361-649 650-1249 1250-2049",
}

VERSIONS = [
    ("2015", EPA_2015, TAD_2018, AQI_7),
    ("2024", EPA_2024, TAD_2024, AQI_6),
]


class TestTables(unittest.TestCase):
    def test_breakpoints_match_the_tad(self):
        """Every band edge gives the AQI of the edge, and back"""
        for version, cls, tad, aqi_bands in VERSIONS:
            algo = cls()
            self.assertEqual(algo.piecewise["aqi"], aqi_bands)
            self.assertEqual(set(algo.piecewise["bp"]), set(tad))
            for elem, spec in tad.items():
                for (aqilo, aqihi), bp in zip(aqi_bands, bands(spec)):
                    if bp is None:
                        continue
                    lo, hi = bp
                    with self.subTest(version=version, elem=elem, band=bp):
                        self.assertEqual(algo.iaqi(elem, str(lo)), aqilo)
                        self.assertEqual(algo.iaqi(elem, str(hi)), aqihi)
                        self.assertEqual(algo.cc(elem, str(aqilo)), lo)
                        self.assertEqual(algo.cc(elem, str(aqihi)), hi)

    def test_stored_tables_are_the_tad_tables(self):
        for version, cls, tad, _ in VERSIONS:
            for elem, spec in tad.items():
                with self.subTest(version=version, elem=elem):
                    stored = [
                        None if bp is None or bp == (0, 0) else bp
                        for bp in cls.piecewise["bp"][elem]
                    ]
                    self.assertEqual(stored, bands(spec))


class TestWorkedExamples(unittest.TestCase):
    """The examples of the TADs (the arithmetic is the same in 2018 and 2024)"""

    def test_ozone_8h(self):
        for cls in (EPA_2015, EPA_2024):
            self.assertEqual(cls().iaqi("o3_8h", "0.07853333"), 126)

    def test_several_pollutants(self):
        for cls in (EPA_2015, EPA_2024):
            with self.subTest(cls=cls.__name__):
                ccs = [("o3_8h", "0.078"), ("pm25", "35.9"), ("co_8h", "8.4")]
                total, iaqis = cls().aqi(ccs, iaqis=True)
                self.assertEqual(iaqis, {"o3_8h": 126, "pm25": 102, "co_8h": 90})
                self.assertEqual(total, 126)

    def test_ozone_1h_and_8h(self):
        # the TAD prints 148, its own arithmetic is 147.49 and rounds to 147
        for cls in (EPA_2015, EPA_2024):
            ccs = [("o3_1h", "0.162"), ("o3_8h", "0.078")]
            self.assertEqual(cls().iaqi("o3_1h", "0.162"), 147)
            self.assertEqual(cls().aqi(ccs), 147)

    def test_blank_places_are_disregarded(self):
        """1 hour ozone under 0.125 is ignored when 8 hour ozone is given"""
        for cls in (EPA_2015, EPA_2024):
            with self.subTest(cls=cls.__name__):
                ccs = [("o3_1h", "0.104"), ("o3_8h", "0.078")]
                total, iaqis = cls().aqi(ccs, iaqis=True)
                self.assertEqual(total, 126)
                self.assertEqual(iaqis, {"o3_8h": 126})

    def test_blank_places_alone(self):
        for cls in (EPA_2015, EPA_2024):
            with self.subTest(cls=cls.__name__):
                with self.assertRaises(NotApplicableError):
                    cls().iaqi("o3_1h", "0.104")
                with self.assertRaises(NotApplicableError):
                    cls().aqi([("o3_1h", "0.104")])
                with self.assertRaises(NotApplicableError):
                    cls().iaqi("o3_1h", "0")
                with self.assertRaises(NotApplicableError):
                    cls().cc("o3_1h", "50")

    def test_not_applicable_is_an_out_of_range_error(self):
        self.assertTrue(issubclass(NotApplicableError, OutOfRangeError))
        self.assertIs(aqi.NotApplicableError, NotApplicableError)

    def test_ozone_1h_bug_15(self):
        """The first bands of 1 hour ozone were (0, 0), 0.125 is AQI 101"""
        for cls in (EPA_2015, EPA_2024):
            self.assertEqual(cls().iaqi("o3_1h", "0.125"), 101)
            self.assertEqual(cls().iaqi("o3_1h", "0.604"), 500)


class TestWhatChanged(unittest.TestCase):
    def test_2015_changes_only_ozone_8h(self):
        for elem, bp in EPA_2012.piecewise["bp"].items():
            if elem not in ("o3_8h", "o3_1h"):
                with self.subTest(elem=elem):
                    self.assertEqual(EPA_2015.piecewise["bp"][elem], bp)
        self.assertEqual(EPA_2015.piecewise["prec"], EPA_2012.piecewise["prec"])
        self.assertEqual(EPA_2015.piecewise["units"], EPA_2012.piecewise["units"])

    def test_ozone_8h_2015(self):
        # 0.060 ppm: Moderate 51-75 in 2012, 0.055-0.070 in 2015
        self.assertEqual(EPA_2012().iaqi("o3_8h", "0.060"), 51)
        self.assertEqual(EPA_2015().iaqi("o3_8h", "0.060"), 67)
        self.assertEqual(EPA_2015().iaqi("o3_8h", "0.070"), 100)
        self.assertEqual(EPA_2015().iaqi("o3_8h", "0.200"), 300)

    def test_pm25_2024(self):
        # 12.1 was the start of Moderate, 9.1 is since 2024
        self.assertEqual(EPA_2015().iaqi("pm25", "12.1"), 51)
        self.assertEqual(EPA_2024().iaqi("pm25", "12.1"), 57)
        self.assertEqual(EPA_2024().iaqi("pm25", "9.0"), 50)
        self.assertEqual(EPA_2024().iaqi("pm25", "9.1"), 51)
        self.assertEqual(EPA_2024().iaqi("pm25", "225.5"), 301)
        self.assertEqual(EPA_2024().iaqi("pm25", "325.4"), 500)

    def test_2024_has_a_single_hazardous_category(self):
        """301-500 is one linear band, so PM10 at 504 is not 400 anymore"""
        self.assertEqual(EPA_2015().iaqi("pm10", "504"), 400)
        self.assertEqual(EPA_2024().iaqi("pm10", "504"), 389)

    def test_2024_beyond_the_aqi(self):
        """Footnote 4: equation 1 with the concentration of AQI 500"""
        with self.assertRaises(OutOfRangeError):
            EPA_2024().iaqi("pm25", "325.5")
        # (500 - 301) / (325.4 - 225.5) * (425.4 - 225.5) + 301 = 699.2
        self.assertEqual(EPA_2024().iaqi("pm25", "425.4", extrapolate=True), 699)
        self.assertEqual(EPA_2024().iaqi("pm25", "326.0", extrapolate=True), 501)
        self.assertEqual(
            EPA_2024().cc("pm25", "699", extrapolate=True), Decimal("425.3")
        )


class TestSelection(unittest.TestCase):
    def test_versions(self):
        self.assertEqual(list(aqi.algos.epa.VERSIONS), ["2012", "2015", "2024"])
        self.assertIs(EPA, EPA_2024)
        self.assertTrue(issubclass(EPA_2024, EPA_2015))
        self.assertTrue(issubclass(EPA_2015, EPA_2012))

    def test_names_and_constants(self):
        self.assertEqual(aqi.ALGO_EPA_2015, "epa:2015")
        self.assertEqual(aqi.ALGO_EPA_2024, "epa:2024")
        for name, cls in (("epa:2015", EPA_2015), ("epa:2024", EPA_2024)):
            self.assertIn(name, aqi.available_algos())
            self.assertIsInstance(aqi.algos.get_algo(name), cls)

    def test_default_is_the_latest(self):
        self.assertIsInstance(aqi.algos.get_algo(aqi.ALGO_EPA), EPA_2024)
        self.assertIsInstance(aqi.algos.get_algo("epa"), EPA_2024)
        self.assertEqual(aqi.to_iaqi("pm25", "12.1"), 57)
        self.assertEqual(aqi.to_iaqi("pm25", "12.1", algo=aqi.ALGO_EPA_2012), 51)

    def test_docstrings_cite_their_source(self):
        for cls, needle in (
            (EPA_2015, "EPA-454/B-18-007"),
            (EPA_2024, "EPA-403/B-26-003"),
        ):
            self.assertIn(needle, cls.__doc__)
