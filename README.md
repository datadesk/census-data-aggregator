# census-data-aggregator

Combine U.S. census data responsibly

### Features

* Approximating sums
* Approximating medians

### Installation

```bash
$ pipenv install census-data-aggregator
```

### Usage

Import the library.

```python
>>> import census_data_aggregator
```

#### Approximating sums

Sum estimates from the U.S. Census Bureau and approximate the combined margin of error. Follows the U.S. Census Bureau's [official guidelines](https://www.documentcloud.org/documents/6162551-20180418-MOE.html) for how to calculate a new margin of error when totaling multiple values. Useful for aggregating census categories and geographies.

Accepts an open-ended set of paired lists, each expected to provide an estimate followed by its margin of error.

```python
>>> males_under_5, males_under_5_moe = 10154024, 3778
>>> females_under_5, females_under_5_moe = 9712936, 3911
>>> census_data_aggregator.approximate_sum(
    (males_under_5, males_under_5_moe),
    (females_under_5, females_under_5_moe)
)
19866960, 5437.757350231803
```

#### Approximating medians

Estimate a median and approximate the margin of error. Follows the U.S. Census Bureau's official guidelines for estimation using a design factor. Useful for generating medians for measures like household income and age when aggregating census geographies.

Expects a list of dictionaries that divide the full range of data values into continuous categories. Each dictionary should have three keys:

| key | value                                                               |
|-----|---------------------------------------------------------------------|
| min | The minimum value of the range                                      |
| max | The maximum value of the range                                      |
| n   | The number of people, households or other units in the range        |

The minimum value in the first range and the maximum value in the last range can be tailored to the dataset by using the "jam values" provided in the [American Community Survey's technical documentation](https://www.documentcloud.org/documents/6165752-2017-SummaryFile-Tech-Doc.html#document/p20/a508561).

```python
>>> income = [
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
```

For a margin of error to be returned, a "design factor" must be provided to calculate the standard error. The statistical input is used to tailor the estimate to the variance of the dataset. The Census Bureau publishes design factors as part of its PUMS Accuracy statement. Find the value for the dataset you are estimating by referring to [the bureau's reference material](https://www.census.gov/programs-surveys/acs/technical-documentation/pums/documentation.html).

```python
>>> census_data_aggregator.approximate_median(income, design_factor=1.5)
42211.096153846156, 27260.315546093672
```

If a design factor is not provided, no margin of error will be returned.

```python
>>> census_data_aggregator.approximate_median(income)
42211.096153846156, None
```

### A note from the experts

The California State Data Center's Demographic Research Unit [notes](https://www.documentcloud.org/documents/6165014-How-to-Recalculate-a-Median.html#document/p4/a508562):

> The user should be aware that the formulas are actually approximations that overstate the MOE compared to the more precise methods based on the actual survey returns that the Census Bureau uses. Therefore, the calculated MOEs will be higher, or more conservative, than those found in published tabulations for similarly-sized areas. This knowledge may affect the level of error you are willing to accept.

### References

This module was designed to conform with the Census Bureau's April 18, 2018, presentation ["Using American Community Survey Estimates and Margin of Error"](https://www.documentcloud.org/documents/6162551-20180418-MOE.html), the bureau's [PUMS Accuracy statement](https://www.documentcloud.org/documents/6165603-2013-2017AccuracyPUMS.html) and the California State Data Center's 2016 edition of ["Recalculating medians and their margins of error for aggregated ACS data."](https://www.documentcloud.org/documents/6165014-How-to-Recalculate-a-Median.html)
