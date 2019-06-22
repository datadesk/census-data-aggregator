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

Returns the combined sum of all the provided Census Bureau estimates, along with an approximated margin of error. Useful when aggregating census categories or geographies. 

Accepts a series of arguments, each a paired list with the estimated value first and the margin of error second.

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

Returns the estimated median from a set of ranged totals, along with an approximated margin of error. Useful for generating medians for measures like household income and age when aggregating census geographies.

Expects a list of dictionaries with three keys:

| key | value                                                               |
|-----|---------------------------------------------------------------------|
| min | The minimum value of the range                                      |
| max | The maximum value of the range                                      |
| n   | The number of people, households or other observations in the range |

For a margin of error to be returned, a "design factor" must be provided to calculate the standard error. Design factors for different census surveys and tables can be found in [the "PUMS Accuracy" CSV files](https://www.census.gov/programs-surveys/acs/technical-documentation/pums/documentation.html).

```python
>>> income = [
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
>>> census_data_aggregator.approximate_median(income, design_factor=1.5)
42211.096153846156, 27260.315546093672
```

If a design factor is not provided, no margin of error will be returned.

```python
>>> census_data_aggregator.approximate_median(income)
42211.096153846156, None
```

### References

This module was designed to conform with the Census Bureau's April 18, 2018, presentation ["Using American Community Survey Estimates and Margin of Error"](https://www.documentcloud.org/documents/6162551-20180418-MOE.html) and the California State Data Center's 2016 edition of ["Recalculating medians and their margins of error for aggregated ACS data."](https://www.documentcloud.org/documents/6165014-How-to-Recalculate-a-Median.html)
