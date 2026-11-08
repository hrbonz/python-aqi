import json
import sys
import unittest
from pathlib import Path

import aqi
from aqi.algos import get_algo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "docs" / "_ext"))

try:
    import aqi_compare
except ImportError:  # docutils is not installed
    aqi_compare = None


@unittest.skipIf(aqi_compare is None, "docutils is not installed")
class TestCompareData(unittest.TestCase):
    def test_every_version_has_metadata(self):
        for name in aqi.available_algos():
            with self.subTest(algo=name):
                info = aqi_compare.VERSIONS[name]
                self.assertTrue(info["standard"])
                self.assertRegex(info["effective"], r"^\d{4}-\d{2}-\d{2}$")

    def test_curves_are_sorted_and_within_scale(self):
        for family in aqi_compare.families():
            data = aqi_compare.build_data(family)
            for elem, entry in data["pollutants"].items():
                for name, info in entry["versions"].items():
                    with self.subTest(algo=name, elem=elem):
                        xs = [p[0] for p in info["curve"]]
                        ys = [p[1] for p in info["curve"]]
                        self.assertEqual(xs, sorted(xs))
                        self.assertEqual(ys, sorted(ys))
                        self.assertGreaterEqual(min(ys), 0)
                        self.assertLessEqual(max(ys), 500)
                        self.assertTrue(info["bands"])

    def test_curve_matches_library(self):
        data = aqi_compare.build_data("epa")
        curve = data["pollutants"]["pm25"]["versions"]["epa:2024"]["curve"]
        self.assertEqual(curve[:3], [[0, 0], [9, 50], [9.1, 51]])
        self.assertEqual([35.4, 100], curve[3])
        algo = get_algo("epa:2024")
        for cc, value in curve:
            self.assertEqual(algo.iaqi("pm25", str(cc)), value)

    def test_html_has_data_and_fallback(self):
        html = aqi_compare.render_html("mep")
        self.assertIn('class="aqi-compare"', html)
        payload = html.split('class="aqi-data">')[1].split("</script>")[0]
        self.assertEqual(json.loads(payload)["family"], "mep")
        for elem in aqi_compare.build_data("mep")["pollutants"]:
            self.assertIn(f'data-elem="{elem}"', html)
        self.assertIn("<table", html)
