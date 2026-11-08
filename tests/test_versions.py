import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
from unittest import mock

import aqi
import aqi.algos
import aqi.algos.epa
import aqi.algos.mep
from aqi.algos.base import PiecewiseAQI, derive_piecewise


class TestGetAlgo(unittest.TestCase):
    def test_module_path_is_latest(self):
        """The historical module names keep working and mean 'latest'"""
        self.assertIsInstance(aqi.algos.get_algo(aqi.ALGO_EPA), aqi.algos.epa.EPA)
        self.assertIsInstance(aqi.algos.get_algo(aqi.ALGO_MEP), aqi.algos.mep.MEP)
        self.assertIsInstance(aqi.algos.get_algo("aqi.algos.epa"), aqi.algos.epa.AQI)

    def test_family_name_is_latest(self):
        self.assertIsInstance(aqi.algos.get_algo("epa"), aqi.algos.epa.EPA)
        self.assertIsInstance(aqi.algos.get_algo("mep"), aqi.algos.mep.MEP)

    def test_versioned_string(self):
        self.assertIsInstance(aqi.algos.get_algo("epa:2012"), aqi.algos.epa.EPA_2012)
        self.assertIsInstance(aqi.algos.get_algo("mep:2012"), aqi.algos.mep.MEP_2012)

    def test_versioned_constants(self):
        self.assertEqual(aqi.ALGO_EPA_2012, "epa:2012")
        self.assertEqual(aqi.ALGO_MEP_2012, "mep:2012")
        self.assertIsInstance(
            aqi.algos.get_algo(aqi.ALGO_EPA_2012), aqi.algos.epa.EPA_2012
        )

    def test_unknown(self):
        for name in ("qwertyuiop", "epa:1900", "nope:2012", "epa:", ":2012", ""):
            with self.subTest(name=name):
                self.assertIsNone(aqi.algos.get_algo(name))

    def test_aliases_are_the_latest_version(self):
        self.assertIs(aqi.algos.epa.EPA, list(aqi.algos.epa.VERSIONS.values())[-1])
        self.assertIs(aqi.algos.epa.AQI, aqi.algos.epa.EPA)
        self.assertIs(aqi.algos.mep.MEP, list(aqi.algos.mep.VERSIONS.values())[-1])
        self.assertIs(aqi.algos.mep.AQI, aqi.algos.mep.MEP)

    def test_public_functions_take_versions(self):
        # PM2.5 12.1 is the start of Moderate in 2012, not anymore in 2024
        expected = {
            aqi.ALGO_EPA: (57, "12.3"),
            "epa": (57, "12.3"),
            "epa:2012": (51, "12.1"),
            aqi.ALGO_EPA_2012: (51, "12.1"),
        }
        for algo, (iaqi, cc) in expected.items():
            with self.subTest(algo=algo):
                self.assertEqual(aqi.to_iaqi(aqi.POLLUTANT_PM25, "12.1", algo), iaqi)
                self.assertEqual(aqi.to_aqi([(aqi.POLLUTANT_PM25, "12.1")], algo), iaqi)
                self.assertEqual(
                    str(aqi.to_cc(aqi.POLLUTANT_PM25, str(iaqi), algo)), cc
                )

    def test_unknown_algo_in_public_functions(self):
        with self.assertRaises(ValueError):
            aqi.to_iaqi(aqi.POLLUTANT_PM25, "12", algo="epa:1900")


class TestAvailable(unittest.TestCase):
    def test_available_algos(self):
        names = aqi.available_algos()
        self.assertIn("epa:2012", names)
        self.assertIn("mep:2012", names)
        for name in names:
            with self.subTest(name=name):
                self.assertIsNotNone(aqi.algos.get_algo(name))

    def test_oldest_first_per_family(self):
        for family in ("epa", "mep"):
            versions = [n for n in aqi.available_algos() if n.startswith(family + ":")]
            self.assertEqual(versions, sorted(versions))

    def test_list_algos(self):
        listed = dict(aqi.list_algos())
        self.assertEqual(set(listed), set(aqi.available_algos()))
        self.assertIn(aqi.POLLUTANT_PM25, dict(listed["epa:2012"]))


class TestDerive(unittest.TestCase):
    """A new version of a standard only states what changed"""

    parent = aqi.algos.epa.EPA_2012.piecewise

    def test_override_one_pollutant(self):
        new_bp = [(0, 10), (11, 20)]
        child = derive_piecewise(self.parent, bp={aqi.POLLUTANT_PM25: new_bp})
        self.assertEqual(child["bp"][aqi.POLLUTANT_PM25], new_bp)
        for elem in self.parent["bp"]:
            if elem != aqi.POLLUTANT_PM25:
                self.assertEqual(child["bp"][elem], self.parent["bp"][elem])
        self.assertEqual(child["aqi"], self.parent["aqi"])
        self.assertEqual(child["prec"], self.parent["prec"])
        self.assertEqual(child["units"], self.parent["units"])

    def test_parent_untouched(self):
        before = self.parent["bp"][aqi.POLLUTANT_PM25]
        derive_piecewise(self.parent, bp={aqi.POLLUTANT_PM25: [(0, 1)]})
        self.assertIs(self.parent["bp"][aqi.POLLUTANT_PM25], before)

    def test_subclass_with_derived_table(self):
        class Child(aqi.algos.epa.EPA_2012):
            piecewise = derive_piecewise(
                aqi.algos.epa.EPA_2012.piecewise,
                bp={
                    aqi.POLLUTANT_PM25: [
                        (Decimal(0), Decimal(100)),
                        (Decimal(101), Decimal(200)),
                    ]
                },
                prec={aqi.POLLUTANT_PM25: Decimal("1.")},
            )

        self.assertIsInstance(Child(), PiecewiseAQI)
        self.assertEqual(Child().iaqi(aqi.POLLUTANT_PM25, "50"), 25)
        # untouched pollutants behave like the parent
        self.assertEqual(
            Child().iaqi(aqi.POLLUTANT_PM10, "100"),
            aqi.algos.epa.EPA_2012().iaqi(aqi.POLLUTANT_PM10, "100"),
        )


class TestExports(unittest.TestCase):
    def test_all_pollutants_exported(self):
        import aqi.constants

        for name in dir(aqi.constants):
            if name.startswith(("POLLUTANT_", "ALGO_")):
                with self.subTest(name=name):
                    self.assertIn(name, aqi.__all__)
                    self.assertEqual(getattr(aqi, name), getattr(aqi.constants, name))

    def test_all_names_exist(self):
        for name in aqi.__all__:
            with self.subTest(name=name):
                self.assertTrue(hasattr(aqi, name))


class TestConsole(unittest.TestCase):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "argv", ["aqi", *args]):
            with redirect_stdout(out), redirect_stderr(err):
                with self.assertRaises(SystemExit) as ctx:
                    aqi.console_aqi()
        return ctx.exception.code, out.getvalue(), err.getvalue()

    def test_list(self):
        """aqi -l crashed on Python 3 before"""
        code, out, err = self.run_cli("-l")
        self.assertEqual(code, 0, err)
        self.assertIn("epa:2012", out)
        self.assertIn("mep:2012", out)
        self.assertIn("pm25", out)

    def test_selector(self):
        for algo, expected in (
            ("epa:2012", "51"),
            ("epa", "57"),
            ("aqi.algos.epa", "57"),
        ):
            with self.subTest(algo=algo):
                code, out, err = self.run_cli(algo, "pm25:12.1")
                self.assertEqual((code, out.strip()), (0, expected), err)

    def test_unknown_selector(self):
        code, _, err = self.run_cli("epa:1900", "pm25:12")
        self.assertEqual(code, 1)
        self.assertIn("Unknown algorithm", err)
