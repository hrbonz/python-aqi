"""The 2012 classes must answer exactly like python-aqi 0.6.1 did.

``data/legacy_0_6_1.json`` was produced by 0.6.1 itself, see
``data/generate_legacy.py``. Whatever the newer versions of a standard
change, ``EPA_2012`` and ``MEP_2012`` stay as they were.
"""

import json
import os
import unittest

import aqi.algos.epa
import aqi.algos.mep

with open(os.path.join(os.path.dirname(__file__), "data", "legacy_0_6_1.json")) as f:
    LEGACY = json.load(f)

CLASSES = {"epa": aqi.algos.epa.EPA_2012, "mep": aqi.algos.mep.MEP_2012}


class TestLegacy(unittest.TestCase):
    def test_reference_data_is_not_empty(self):
        for family in CLASSES:
            for kind in ("iaqi", "cc"):
                for elem, grid in LEGACY[family][kind].items():
                    with self.subTest(family=family, kind=kind, elem=elem):
                        self.assertGreater(len(grid), 50)

    def test_iaqi(self):
        for family, cls in CLASSES.items():
            algo = cls()
            for elem, grid in LEGACY[family]["iaqi"].items():
                with self.subTest(family=family, elem=elem):
                    for cc, expected in grid.items():
                        self.assertEqual(algo.iaqi(elem, cc), expected, (elem, cc))

    def test_cc(self):
        for family, cls in CLASSES.items():
            algo = cls()
            for elem, grid in LEGACY[family]["cc"].items():
                with self.subTest(family=family, elem=elem):
                    for iaqi, expected in grid.items():
                        self.assertEqual(
                            str(algo.cc(elem, iaqi)), expected, (elem, iaqi)
                        )

    def test_same_pollutants(self):
        for family, cls in CLASSES.items():
            self.assertEqual(
                set(dict(cls().list_pollutants())), set(LEGACY[family]["iaqi"])
            )
