import unittest
import census_data_aggregator



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
                [0, 22],
                [0, 22],
                [0, 29],
                [41, 37]
            ),
            (41, 47.01063709417264)
        )

    def test_median(self):
        income = [
            dict(start=-2500, end=9999, total=186),
            dict(start=10000, end=14999, total=78),
            dict(start=15000, end=19999, total=98),
            dict(start=20000, end=24999, total=287),
            dict(start=25000, end=29999, total=142),
            dict(start=30000, end=34999, total=90),
            dict(start=35000, end=39999, total=107),
            dict(start=40000, end=44999, total=104),
            dict(start=45000, end=49999, total=178),
            dict(start=50000, end=59999, total=106),
            dict(start=60000, end=74999, total=177),
            dict(start=75000, end=99999, total=262),
            dict(start=100000, end=124999, total=77),
            dict(start=125000, end=149999, total=100),
            dict(start=150000, end=199999, total=58),
            dict(start=200000, end=250001, total=18)
        ]
        self.assertEqual(
            census_data_aggregator.approximate_median(income),
            42211.096153846156
        )
