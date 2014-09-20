# -*- coding: utf-8 -*-

import unittest

import aqi.algos.base


class TestBaseAQI(unittest.TestCase):
    """
    Test the base module
    """

    def test_aqi(self):
        """Test the BaseAQI class"""
        _aqi = aqi.algos.base.BaseAQI()
        # dummy iaqi function, return the concentration
        _aqi.iaqi = lambda x, y: int(y)
        self.assertEqual(
            _aqi.aqi([(0, '20'), (1,'30'), (2, '100')]),
            100)
        self.assertEqual(
            _aqi.aqi([(0, '20'), (1,'30'), (2, '100')], iaqis=True),
            (100, {0: 20, 1: 30, 2: 100}))
