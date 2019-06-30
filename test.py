#! /usr/bin/env python
# -*- coding: utf-8 -*-
import doctest
import unittest
import census_data_aggregator
from census_data_aggregator.exceptions import DesignFactorWarning, DataError


class CensusErrorAnalyzerTest(unittest.TestCase):

    def test_sum(self):
        males_under_5, males_under_5_moe = 10154024, 3778
        females_under_5, females_under_5_moe = 9712936, 3911
        self.assertEqual(
            census_data_aggregator.approximate_sum(
                (males_under_5, males_under_5_moe),
                (females_under_5, females_under_5_moe)
            ),
            (19866960, 5437.757350231803)
        )
        # With multiple zeros
        self.assertEqual(
            census_data_aggregator.approximate_sum(
                [0.0, 22],
                [0, 22],
                [0, 29],
                [41, 37]
            ),
            (41, 47.01063709417264)
        )
        # From the ACS handbook examples
        single_women = (
            (135173, 3860),
            (43104, 2642),
            (24842, 1957)
        )
        self.assertEqual(
            census_data_aggregator.approximate_sum(*single_women),
            (203119, 5070.4647715963865)
        )

    def test_median(self):
        income = [
            dict(min=2499, max=9999, n=186),
            dict(min=10000, max=14999, n=78),
            dict(min=15000, max=19999, n=98),
            dict(min=20000, max=24999, n=287),
            dict(min=25000, max=29999, n=142),
            dict(min=30000, max=34999, n=90),
            dict(min=35000, max=39999, n=107),
            dict(min=40000, max=44999, n=104),
            dict(min=45000, max=49999, n=178),
            dict(min=50000, max=59999, n=106),
            dict(min=60000, max=74999, n=177),
            dict(min=75000, max=99999, n=262),
            dict(min=100000, max=124999, n=77),
            dict(min=125000, max=149999, n=100),
            dict(min=150000, max=199999, n=58),
            dict(min=200000, max=250001, n=18)
        ]
        self.assertEqual(
            census_data_aggregator.approximate_median(income, design_factor=1.5),
            (42211.096153846156, 27260.315546093672)
        )

        with self.assertWarns(DesignFactorWarning):
            m, moe = census_data_aggregator.approximate_median(income)
            self.assertTrue(moe == None)

        # Test a sample size so small the p values fail
        with self.assertRaises(DataError):
            bad_data = [
                dict(min=0, max=49999, n=5),
                dict(min=50000, max=99999, n=5),
                dict(min=100000, max=199999, n=5),
                dict(min=200000, max=250001, n=5)
            ]
            census_data_aggregator.approximate_median(bad_data, design_factor=1.5)

        top_median = [
            dict(min=0, max=49999, n=50),
            dict(min=50000, max=99999, n=50),
            dict(min=100000, max=199999, n=50),
            dict(min=200000, max=250001, n=5000)
        ]
        census_data_aggregator.approximate_median(top_median, design_factor=1.5)

    def test_exception(self):
        DesignFactorWarning().__str__()

    def test_sum(self):
        estimate, moe = census_data_aggregator.approximate_sum((379, 1), (384, 1))
        self.assertAlmostEqual(estimate, 763)
        self.assertAlmostEqual(moe, 1.4142135623730951)

    def test_proportion(self):
        estimate, moe = census_data_aggregator.approximate_proportion((379, 1), (384, 1))
        self.assertAlmostEqual(estimate, 0.9869791666666666)
        self.assertAlmostEqual(moe, 0.008208247339752435)

        # From the Census handbook
        estimate, moe = census_data_aggregator.approximate_proportion(
            (203119, 5070),
            (630498, 831)
        )
        self.assertAlmostEqual(estimate, 0.32215645)
        self.assertAlmostEqual(moe, 0.008)

    def test_ratio(self):
        estimate, moe = census_data_aggregator.approximate_ratio((379, 1), (384, 1))
        self.assertAlmostEqual(estimate, 0.9869791666666666)
        self.assertAlmostEqual(moe, 0.07170047425884142)

    def test_product(self):
        estimate, moe = census_data_aggregator.approximate_product((384, 1), (0.987, 0.06))
        self.assertAlmostEqual(estimate, 379.008)
        self.assertAlmostEqual(moe, 23.061131130107213)


if __name__ == '__main__':
    unittest.main()
    doctest.testmod("census_data_aggregator/__init__.py")
