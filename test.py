#! /usr/bin/env python
import doctest
import unittest

import numpy

import census_data_aggregator
from census_data_aggregator.exceptions import DataError, SamplingPercentageWarning


class CensusErrorAnalyzerTest(unittest.TestCase):
    def test_sum(self):
        males_under_5, males_under_5_moe = 10154024, 3778
        females_under_5, females_under_5_moe = 9712936, 3911
        self.assertEqual(
            census_data_aggregator.approximate_sum(
                (males_under_5, males_under_5_moe),
                (females_under_5, females_under_5_moe),
            ),
            (19866960, 5437.757350231803),
        )
        # With multiple zeros
        self.assertEqual(
            census_data_aggregator.approximate_sum(
                [0.0, 22], [0, 22], [0, 29], [41, 37]
            ),
            (41, 47.01063709417264),
        )
        # From the ACS handbook examples
        single_women = ((135173, 3860), (43104, 2642), (24842, 1957))
        self.assertEqual(
            census_data_aggregator.approximate_sum(*single_women),
            (203119, 5070.4647715963865),
        )

    def test_median(self):
        household_income_Los_Angeles_County_2013_acs5 = [
            dict(min=2499, max=9999, n=209050),
            dict(min=10000, max=14999, n=190300),
            dict(min=15000, max=19999, n=173380),
            dict(min=20000, max=24999, n=167740),
            dict(min=25000, max=29999, n=154347),
            dict(min=30000, max=34999, n=155834),
            dict(min=35000, max=39999, n=143103),
            dict(min=40000, max=44999, n=140946),
            dict(min=45000, max=49999, n=126807),
            dict(min=50000, max=59999, n=241482),
            dict(min=60000, max=74999, n=303887),
            dict(min=75000, max=99999, n=384881),
            dict(min=100000, max=124999, n=268689),
            dict(min=125000, max=149999, n=169129),
            dict(min=150000, max=199999, n=189195),
            dict(min=200000, max=250001, n=211613),
        ]

        self.assertEqual(
            census_data_aggregator.approximate_median(
                household_income_Los_Angeles_County_2013_acs5,
                sampling_percentage=2.5 * 5,
            ),
            (56363.58534176461, 161.96723586588095),
        )

        household_income_Los_Angeles_County_2013_acs3 = [
            dict(min=2499, max=9999, n=222966),
            dict(min=10000, max=14999, n=197354),
            dict(min=15000, max=19999, n=178836),
            dict(min=20000, max=24999, n=177895),
            dict(min=25000, max=29999, n=155399),
            dict(min=30000, max=34999, n=156869),
            dict(min=35000, max=39999, n=145396),
            dict(min=40000, max=44999, n=141772),
            dict(min=45000, max=49999, n=125984),
            dict(min=50000, max=59999, n=237511),
            dict(min=60000, max=74999, n=303531),
            dict(min=75000, max=99999, n=371986),
            dict(min=100000, max=124999, n=264049),
            dict(min=125000, max=149999, n=164391),
            dict(min=150000, max=199999, n=179788),
            dict(min=200000, max=250001, n=209815),
        ]

        self.assertEqual(
            census_data_aggregator.approximate_median(
                household_income_Los_Angeles_County_2013_acs3,
                sampling_percentage=2.5 * 3,
            ),
            (54811.92744757085, 218.6913805834877),
        )

        household_income_la_2013_acs1 = [
            dict(min=2499, max=9999, n=1382),
            dict(min=10000, max=14999, n=2377),
            dict(min=15000, max=19999, n=1332),
            dict(min=20000, max=24999, n=3129),
            dict(min=25000, max=29999, n=1927),
            dict(min=30000, max=34999, n=1825),
            dict(min=35000, max=39999, n=1567),
            dict(min=40000, max=44999, n=1996),
            dict(min=45000, max=49999, n=1757),
            dict(min=50000, max=59999, n=3523),
            dict(min=60000, max=74999, n=4360),
            dict(min=75000, max=99999, n=6424),
            dict(min=100000, max=124999, n=5257),
            dict(min=125000, max=149999, n=3485),
            dict(min=150000, max=199999, n=2926),
            dict(min=200000, max=250001, n=4215),
        ]

        self.assertEqual(
            census_data_aggregator.approximate_median(
                household_income_la_2013_acs1, sampling_percentage=2.5
            ),
            (70065.84266055046, 3850.680465234964),
        )

        with self.assertWarns(SamplingPercentageWarning):
            m, moe = census_data_aggregator.approximate_median(
                household_income_Los_Angeles_County_2013_acs5, design_factor=1.5
            )
            self.assertTrue(moe is None)
        # Test a sample size so small the p values fail
        with self.assertRaises(DataError):
            bad_data = [
                dict(min=0, max=49999, n=5),
                dict(min=50000, max=99999, n=5),
                dict(min=100000, max=199999, n=5),
                dict(min=200000, max=250001, n=5),
            ]
            census_data_aggregator.approximate_median(
                bad_data, design_factor=1.5, sampling_percentage=1
            )

        top_median = [
            dict(min=0, max=49999, n=50),
            dict(min=50000, max=99999, n=50),
            dict(min=100000, max=199999, n=50),
            dict(min=200000, max=250001, n=5000),
        ]
        census_data_aggregator.approximate_median(
            top_median, design_factor=1.5, sampling_percentage=1
        )

    def test_percentchange(self):
        estimate, moe = census_data_aggregator.approximate_percentchange(
            (135173, 3860), (139301, 4047)
        )
        self.assertAlmostEqual(estimate, 3.0538643072211165)
        self.assertAlmostEqual(moe, 4.198069852261231)

    def test_sum_ch8(self):
        # Never-married female characteristics from Table 8.1
        nmf_fairfax = (135173, 3860)
        nmf_arlington = (43104, 2642)
        nmf_alexandria = (24842, 1957)

        # Calculate aggregate pop and MOE
        agg_pop, agg_moe = census_data_aggregator.approximate_sum(
            nmf_fairfax, nmf_arlington, nmf_alexandria
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
            tf15_fairfax, tf15_arlington, tf15_alexandria
        )

        numerator = (203119, 5070)

        # Calculate the proportion and its MOE
        proportion, moe = census_data_aggregator.approximate_proportion(
            numerator, denominator
        )

        self.assertAlmostEqual(proportion, 0.322, places=3)
        self.assertAlmostEqual(moe, 0.008, places=3)

        with self.assertRaises(DataError):
            census_data_aggregator.approximate_proportion(denominator, numerator)

    def test_ratio_ch8(self):
        # Never-married Males from table 8.5
        nmm_fairfax = (156720, 4222)
        nmm_arlington = (44613, 2819)
        nmm_alexandria = (25507, 2259)

        # Aggregate the values and MOEs
        numerator = census_data_aggregator.approximate_sum(
            nmm_fairfax, nmm_arlington, nmm_alexandria
        )

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

        (
            num_1unit_det_oou_est,
            num_1unit_det_oou_moe,
        ) = census_data_aggregator.approximate_product(oou, pct_1unit_det_oou)

        self.assertAlmostEqual(num_1unit_det_oou_est, 61393366, places=0)
        self.assertAlmostEqual(num_1unit_det_oou_moe, 202289, places=0)

    def test_mean(self):
        range_list = [
            dict(min=0, max=9999, n=7942251, moe=17662),
            dict(min=10000, max=14999, n=5768114, moe=16409),
            dict(min=15000, max=19999, n=5727180, moe=16801),
            dict(min=20000, max=24999, n=5910725, moe=17864),
            dict(min=25000, max=29999, n=5619002, moe=16113),
            dict(min=30000, max=34999, n=5711286, moe=15891),
            dict(min=35000, max=39999, n=5332778, moe=16488),
            dict(min=40000, max=44999, n=5354520, moe=15415),
            dict(min=45000, max=49999, n=4725195, moe=16890),
            dict(min=50000, max=59999, n=9181800, moe=20965),
            dict(min=60000, max=74999, n=11818514, moe=30723),
            dict(min=75000, max=99999, n=14636046, moe=49159),
            dict(min=100000, max=124999, n=10273788, moe=47842),
            dict(min=125000, max=149999, n=6428069, moe=37952),
            dict(min=150000, max=199999, n=6931136, moe=37236),
            dict(min=200000, max=1000000, n=7465517, moe=42206),
        ]
        numpy.random.seed(711355)
        # Calculate the mean and its MOE
        mean, moe = census_data_aggregator.approximate_mean(range_list)

        self.assertAlmostEqual(mean, 98045.44530685373, places=3)
        self.assertAlmostEqual(moe, 194.54892406267754, places=3)

        numpy.random.seed(711355)

        mean, moe = census_data_aggregator.approximate_mean(range_list, pareto=True)

        self.assertAlmostEqual(mean, 60364.96525340687, places=3)
        self.assertAlmostEqual(moe, 58.60735554621351, places=3)

    def test_mean_order(self):
        range_list = [
            dict(min=50000, max=59999, n=9181800, moe=20965),
            dict(min=60000, max=74999, n=11818514, moe=30723),
            dict(min=75000, max=99999, n=14636046, moe=49159),
            dict(min=100000, max=124999, n=10273788, moe=47842),
            dict(min=125000, max=149999, n=6428069, moe=37952),
            dict(min=150000, max=199999, n=6931136, moe=37236),
            dict(min=200000, max=1000000, n=7465517, moe=42206),
            dict(min=0, max=9999, n=7942251, moe=17662),
            dict(min=10000, max=14999, n=5768114, moe=16409),
            dict(min=15000, max=19999, n=5727180, moe=16801),
            dict(min=20000, max=24999, n=5910725, moe=17864),
            dict(min=25000, max=29999, n=5619002, moe=16113),
            dict(min=30000, max=34999, n=5711286, moe=15891),
            dict(min=35000, max=39999, n=5332778, moe=16488),
            dict(min=40000, max=44999, n=5354520, moe=15415),
            dict(min=45000, max=49999, n=4725195, moe=16890),
        ]
        numpy.random.seed(711355)
        # Calculate the mean and its MOE
        mean, moe = census_data_aggregator.approximate_mean(range_list)

        self.assertAlmostEqual(mean, 98045.44530685373, places=3)
        self.assertAlmostEqual(moe, 194.54892406267754, places=3)

        numpy.random.seed(711355)

        mean, moe = census_data_aggregator.approximate_mean(range_list, pareto=True)

        self.assertAlmostEqual(mean, 60364.96525340687, places=3)
        self.assertAlmostEqual(moe, 58.60735554621351, places=3)


if __name__ == "__main__":
    unittest.main()
    doctest.testmod("census_data_aggregator/__init__.py")
