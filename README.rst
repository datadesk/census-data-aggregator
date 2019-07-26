census-data-aggregator
======================

Combine U.S. census data responsibly


Features
^^^^^^^^

* Approximating sums
* Approximating medians
* Approximating percent change
* Approximating products
* Approximating proportions
* Approximating ratios


Installation
^^^^^^^^^^^^

.. code-block:: bash

   $ pipenv install census-data-aggregator


Usage
^^^^^

Import the library.

.. code-block:: python

   >>> import census_data_aggregator


Approximating sums
~~~~~~~~~~~~~~~~~~

Total together estimates from the U.S. Census Bureau and approximate the combined margin of error. Follows the bureau's `official guidelines <https://www.documentcloud.org/documents/6162551-20180418-MOE.html>`_ for how to calculate a new margin of error when totaling multiple values. Useful for aggregating census categories and geographies.

Accepts an open-ended set of paired lists, each expected to provide an estimate followed by its margin of error.

.. code-block:: python

  >>> males_under_5, males_under_5_moe = 10154024, 3778
  >>> females_under_5, females_under_5_moe = 9712936, 3911
  >>> census_data_aggregator.approximate_sum(
      (males_under_5, males_under_5_moe),
      (females_under_5, females_under_5_moe)
  )
  19866960, 5437.757350231803


Approximating medians
~~~~~~~~~~~~~~~~~~~~~

Estimate a median and approximate the margin of error. Follows the U.S. Census Bureau's official guidelines for estimation. Useful for generating medians for measures like household income and age when aggregating census geographies.

Expects a list of dictionaries that divide the full range of data values into continuous categories. Each dictionary should have three keys:

.. list-table::
  :header-rows: 1

  * - key
    - value
  * - min
    - The minimum value of the range
  * - max
    - The maximum value of the range
  * - n
    - The number of people, households or other units in the range


The minimum value in the first range and the maximum value in the last range can be tailored to the dataset by using the "jam values" provided in the `American Community Survey's technical documentation <https://www.documentcloud.org/documents/6165752-2017-SummaryFile-Tech-Doc.html#document/p20/a508561>`_.

.. code-block:: python

  >>> household_income_la_2013_acs1 = [
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
      dict(min=200000, max=250001, n=4215)
  ]

For a margin of error to be returned, a sampling percentage must be provided to calculate the standard error. The sampling percentage represents what proportion of the population that participated in the survey. Here are the values for some common census surveys.

.. list-table::
  :header-rows: 1

  * - survey
    - samping percentage
  * - One-year PUMS
    - 1
  * - One-year ACS
    - 2.5
  * - Three-year ACS
    - 7.5
  * - Five-year ACS
    - 12.5

.. code-block:: python

    >>> census_data_aggregator.approximate_median(household_income_Los_Angeles_County_2013_acs1, sampling_percentage=2.5)
    70065.84266055046, 3850.680465234964

If you do not provide the value to the function, no margin of error will be returned.

.. code-block:: python

  >>> census_data_aggregator.approximate_median(household_income_Los_Angeles_County_2013_acs1)
  70065.84266055046, None

If the data being approximated comes from PUMS, a additional design factor must also be provided. The design factor is a statistical input used to tailor the estimate to the variance of the dataset. Find the value for the dataset you are estimating by referring to `the bureau's reference material <https://www.census.gov/programs-surveys/acs/technical-documentation/pums/documentation.html>`_.


Approximating percent change
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Calculates the percent change between two estimates and approximates its margin of error. Follows the bureau's `ACS handbook <https://www.documentcloud.org/documents/6177941-Acs-General-Handbook-2018-ch08.html>`_.

Accepts two paired lists, each expected to provide an estimate followed by its margin of error. The first input should be the earlier estimate in the comparison. The second input should be the later estimate.

Returns both values as percentages multiplied by 100.

.. code-block:: python

    >>> single_women_in_fairfax_before = 135173, 3860
    >>> single_women_in_fairfax_after = 139301, 4047
    >>> census_data_aggregator.approximate_percentchange(
      single_women_in_fairfax_before,
      single_women_in_fairfax_after
    )
    3.0538643072211165, 4.198069852261231


Approximating products
~~~~~~~~~~~~~~~~~~~~~~

Calculates the product of two estimates and approximates its margin of error. Follows the bureau's `ACS handbook <https://www.documentcloud.org/documents/6177941-Acs-General-Handbook-2018-ch08.html>`_.

Accepts two paired lists, each expected to provide an estimate followed by its margin of error.

.. code-block:: python

   >>> owner_occupied_units = 74506512, 228238
   >>> single_family_percent = 0.824, 0.001
   >>> census_data_aggregator.approximate_product(
       owner_occupied_units,
       single_family_percent
   )
   61393366, 202289


Approximating proportions
~~~~~~~~~~~~~~~~~~~~~~~~~

Calculate an estimate's proportion of another estimate and approximate the margin of error. Follows the bureau's `ACS handbook <https://www.documentcloud.org/documents/6177941-Acs-General-Handbook-2018-ch08.html>`_. Simply multiply the result by 100 for a percentage. Recommended when the first value is smaller than the second.

Accepts two paired lists, each expected to provide an estimate followed by its margin of error. The numerator goes in first. The denominator goes in second. In cases where the numerator is not a subset of the denominator, the bureau recommends using the approximate_ratio method instead.

.. code-block:: python

  >>> single_women_in_virginia = 203119, 5070
  >>> total_women_in_virginia = 690746, 831
  >>> census_data_aggregator.approximate_proportion(
      single_women_in_virginia,
      total_women_in_virginia
  )
  0.322, 0.008


Approximating ratios
~~~~~~~~~~~~~~~~~~~~

Calculate the ratio between two estimates and approximate its margin of error. Follows the bureau's `ACS handbook <https://www.documentcloud.org/documents/6177941-Acs-General-Handbook-2018-ch08.html>`_.

Accepts two paired lists, each expected to provide an estimate followed by its margin of error. The numerator goes in first. The denominator goes in second. In cases where the numerator is a subset of the denominator, the bureau recommends uses the approximate_proportion method.

.. code-block:: python

  >>> single_men_in_virginia = 226840, 5556
  >>> single_women_in_virginia = 203119, 5070
  >>> census_data_aggregator.approximate_ratio(
      single_men_in_virginia,
      single_women_in_virginia
  )
  1.117, 0.039


A note from the experts
^^^^^^^^^^^^^^^^^^^^^^^

The California State Data Center's Demographic Research Unit `notes <https://www.documentcloud.org/documents/6165014-How-to-Recalculate-a-Median.html#document/p4/a508562>`_\ :

..

   The user should be aware that the formulas are actually approximations that overstate the MOE compared to the more precise methods based on the actual survey returns that the Census Bureau uses. Therefore, the calculated MOEs will be higher, or more conservative, than those found in published tabulations for similarly-sized areas. This knowledge may affect the level of error you are willing to accept.


The American Community Survey's handbook `adds <https://www.documentcloud.org/documents/6177941-Acs-General-Handbook-2018-ch08.html#document/p3/a509993>`_\ :

..

   As the number of estimates involved in a sum or difference increases, the results of the approximation formula become increasingly different from the [standard error] derived directly from the ACS microdata. Users are encouraged to work with the fewest number of estimates possible.


References
^^^^^^^^^^

This module was designed to conform with the Census Bureau's April 18, 2018, presentation `"Using American Community Survey Estimates and Margin of Error" <https://www.documentcloud.org/documents/6162551-20180418-MOE.html>`_\ , the bureau's `PUMS Accuracy statement <https://www.documentcloud.org/documents/6165603-2013-2017AccuracyPUMS.html>`_ and the California State Data Center's 2016 edition of `"Recalculating medians and their margins of error for aggregated ACS data." <https://www.documentcloud.org/documents/6165014-How-to-Recalculate-a-Median.html>`_\ , and the Census Bureau's `ACS 2018 General Handbook Chapter 8, "Calculating Measures of Error for Derived Estimates" <https://www.documentcloud.org/documents/6177941-Acs-General-Handbook-2018-ch08.html>`_
