# -*- coding: utf-8 -*-

import unittest

import aqi.algos
import aqi.algos.epa
import aqi.constants


class TestAlgos(unittest.TestCase):
    """
    Test the aqi.algo module
    """

    def test_get_algo(self):
        """Test algo loading"""
        self.assertIsNone(
            aqi.algos.get_algo('qwertyuiop'))
        self.assertIsInstance(
            aqi.algos.get_algo(aqi.constants.ALGO_EPA),
            aqi.algos.epa.AQI)
