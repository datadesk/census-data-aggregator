#! /usr/bin/env python
# -*- coding: utf-8 -*-
import doctest
import unittest
import census_data_aggregator
from census_data_aggregator.exceptions import (
    DesignFactorWarning,
    DataError,
    SamplingPercentageWarning
)


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
            census_data_aggregator.approximate_median(income, design_factor=1.5, sampling_percentage=1),
            (42211.096153846156, 27260.315546093672)
        )

        with self.assertWarns(DesignFactorWarning):
            m, moe = census_data_aggregator.approximate_median(income)
            self.assertTrue(moe == None)
 
        with self.assertWarns(DesignFactorWarning):
            m, moe = census_data_aggregator.approximate_median(income, sampling_percentage=1)
            self.assertTrue(moe == None)
        
        with self.assertWarns(SamplingPercentageWarning):
            m, moe = census_data_aggregator.approximate_median(income, design_factor=1.5)
            self.assertTrue(moe == None)    
        # Test a sample size so small the p values fail
        with self.assertRaises(DataError):
            bad_data = [
                dict(min=0, max=49999, n=5),
                dict(min=50000, max=99999, n=5),
                dict(min=100000, max=199999, n=5),
                dict(min=200000, max=250001, n=5)
            ]
            census_data_aggregator.approximate_median(bad_data, design_factor=1.5, sampling_percentage=1)

        top_median = [
            dict(min=0, max=49999, n=50),
            dict(min=50000, max=99999, n=50),
            dict(min=100000, max=199999, n=50),
            dict(min=200000, max=250001, n=5000)
        ]
        census_data_aggregator.approximate_median(top_median, design_factor=1.5, sampling_percentage=1)

    def test_percentchange(self):
        estimate, moe = census_data_aggregator.approximate_percentchange(
            (135173, 3860),
            (139301, 4047)
        )
        self.assertAlmostEqual(estimate, 3.0538643072211165)
        self.assertAlmostEqual(moe, 4.198069852261231)

    def test_exception(self):
        DesignFactorWarning().__str__()

    def test_sum_ch8(self):
        # Never-married female characteristics from Table 8.1
        nmf_fairfax = (135173, 3860)
        nmf_arlington = (43104, 2642)
        nmf_alexandria = (24842, 1957)

        # Calculate aggregate pop and MOE
        agg_pop, agg_moe = census_data_aggregator.approximate_sum(
            nmf_fairfax,
            nmf_arlington,
            nmf_alexandria
        )

        self.assertEqual(agg_pop, 203119)
        self.assertAlmostEqual(agg_moe, 5070, places=0)

    def test_proportion_ch8(self):
        # Total females aged 15 and older from Table 8.4
        tf15_fairfax = (466037, 391)
        tf15_arlington = (97360, 572)
        tf15_alexandria = (67101, 459)

        # Aggregate the values and MOEs
        denominator = census_data_aggregator.approximate_sum(
            tf15_fairfax,
            tf15_arlington,
            tf15_alexandria
        )

        numerator = (203119, 5070)

        # Calculate the proportion and its MOE
        proportion, moe = census_data_aggregator.approximate_proportion(
            numerator,
            denominator
        )

        self.assertAlmostEqual(proportion, 0.322, places=3)
        self.assertAlmostEqual(moe, 0.008, places=3)

        with self.assertRaises(DataError):
            census_data_aggregator.approximate_proportion(
                denominator,
                numerator
            )

    def test_ratio_ch8(self):
        # Never-married Males from table 8.5
        nmm_fairfax = (156720, 4222)
        nmm_arlington = (44613, 2819)
        nmm_alexandria = (25507, 2259)

        # Aggregate the values and MOEs
        numerator = census_data_aggregator.approximate_sum(nmm_fairfax, nmm_arlington, nmm_alexandria)

        denominator = (203119, 5070)

        # Calculate the proportion and its MOE
        ratio, moe = census_data_aggregator.approximate_ratio(numerator, denominator)

        self.assertAlmostEqual(ratio, 1.117, places=3)
        self.assertAlmostEqual(moe, 0.039, places=3)

    def test_product_ch8(self):
        # Number of owner-occupied housing units in the United States
        oou = (74506512, 228238)
        # Percentage of single-unit, owner-occupied housing units in the United States
        pct_1unit_det_oou = (0.824, 0.001)

        num_1unit_det_oou_est, num_1unit_det_oou_moe = \
            census_data_aggregator.approximate_product(oou, pct_1unit_det_oou)

        self.assertAlmostEqual(num_1unit_det_oou_est, 61393366, places=0)
        self.assertAlmostEqual(num_1unit_det_oou_moe, 202289, places=0)


if __name__ == '__main__':
    unittest.main()
    doctest.testmod("census_data_aggregator/__init__.py")
