import unittest
import census_data_aggregator
from census_data_aggregator.exceptions import DesignFactorWarning


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

    def test_median(self):
        income = [
            dict(min=-2500, max=9999, n=186),
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
            census_data_aggregator.approximate_median(income)



if __name__ == '__main__':
    unittest.main()
