import os
import sys
import unittest

import aqi

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "docs", "_ext"))

try:
    import aqi_tables
except ImportError:  # docutils is in the docs dependency group
    aqi_tables = None


@unittest.skipIf(aqi_tables is None, "docutils is not installed")
class TestBreakpointTables(unittest.TestCase):
    """The tables of the documentation are built from the library"""

    def test_every_version(self):
        for name in aqi.available_algos():
            with self.subTest(name=name):
                header, rows = aqi_tables.build_rows(name)
                algo = aqi.algos.get_algo(name)
                self.assertEqual(len(header), 1 + len(algo.piecewise["aqi"]))
                self.assertEqual(len(rows), len(algo.piecewise["bp"]))
                for row in rows:
                    self.assertEqual(len(row), len(header))

    def test_values(self):
        _, rows = aqi_tables.build_rows("epa:2024")
        pm25 = next(row for row in rows if row[0].startswith("pm25"))
        self.assertEqual(pm25[1], "0.0 – 9.0")
        self.assertEqual(pm25[-1], "225.5 – 325.4")
        o3_1h = next(row for row in rows if row[0].startswith("o3_1h"))
        self.assertEqual(o3_1h[1:3], ["–", "–"])

    def test_unknown_algorithm(self):
        with self.assertRaises(ValueError):
            aqi_tables.build_rows("epa:1900")
