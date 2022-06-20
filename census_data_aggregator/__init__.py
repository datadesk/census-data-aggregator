import math
import warnings

import numpy

from .exceptions import DataError, SamplingPercentageWarning


def approximate_sum(*pairs):
    """Sum estimates from the U.S. Census Bureau and approximate the combined margin of error.

    Follows the U.S. Census Bureau's `official guidelines`_ for how to calculate a new margin of error
    when totaling multiple values. Useful for aggregating census categories and geographies.

    Args:
        *pairs (list): An open-ended set of paired lists, each expected to provide an
            estimate followed by its margin of error.

    Returns:
        A two-item tuple with the summed total followed by the approximated margin of error.

        (19866960, 5437.757350231803)

    Examples:
        Combining the under-five male population with under-five female population
        to calculate a grand total of children under five.

        >>> males_under_5, males_under_5_moe = 10154024, 3778
        >>> females_under_5, females_under_5_moe = 9712936, 3911
        >>> approximate_sum(
            (males_under_5, males_under_5_moe),
            (females_under_5, females_under_5_moe)
        )
        19866960, 5437.757350231803

    .. _official guidelines:
        https://www.documentcloud.org/documents/6162551-20180418-MOE.html
    """
    # According to the Census Bureau, when approximating a sum use only the largest zero estimate margin of error, once
    # https://www.documentcloud.org/documents/6162551-20180418-MOE.html#document/p52
    zeros = [p for p in pairs if p[0] == 0]
    # So if there are zeros...
    if len(zeros) > 1:
        # ... weed them out
        max_zero_margin = max(p[1] for p in zeros)
        not_zero_margins = [p[1] for p in pairs if p[0] != 0]
        margins = [max_zero_margin] + not_zero_margins
    # If not, just keep all the input margins
    else:
        margins = [p[1] for p in pairs]

    # Calculate the margin using the bureau's official formula
    margin_of_error = math.sqrt(sum(m**2 for m in margins))

    # Calculate the total
    total = sum(p[0] for p in pairs)

    # Return the results
    return total, margin_of_error


def approximate_median(range_list, design_factor=1, sampling_percentage=None):
    """Estimate a median and approximate the margin of error.

    Follows the U.S. Census Bureau's `official guidelines`_ for estimation using a design factor.
    Useful for generating medians for measures like household income and age when aggregating census geographies.

    Args:
        range_list (list): A list of dictionaries that divide the full range of data values into continuous categories.
            Each dictionary should have three keys:
                * min (int): The minimum value of the range
                * max (int): The maximum value of the range
                * n (int): The number of people, households or other unit in the range
            The minimum value in the first range and the maximum value in the last range
            can be tailored to the dataset by using the "jam values" provided in
            the `American Community Survey's technical documentation`_.
        design_factor (float, optional): A statistical input used to tailor the standard error to the
            variance of the dataset. This is only needed for data coming from public use microdata sample,
            also known as PUMS. You do not need to provide this input if you are approximating
            data from the American Community Survey. The design factor for each PUMS
            dataset is provided as part of `the bureau's reference material`_.
        sampling_percentage (float, optional): A statistical input used to correct for variance linked to
            the size of the survey's population sample. This value submitted should be the percentage of
            * One-year PUMS: 1
            * One-year ACS: 2.5
            * Three-year ACS: 7.5
            * Five-year ACS: 12.5
         If you do not provide this input, a margin of error will not be returned.

    Returns:
        A two-item tuple with the median followed by the approximated margin of error.

        (42211.096153846156, 10153.200960954948)

    Examples:
        Estimating the median for a range of household incomes.

        >>> household_income_2013_acs5 = [
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

        >>> approximate_median(household_income_2013_acs5, sampling_percentage=5*2.5)
        (42211.096153846156, 4706.522752733644)

    ... _official guidelines:
        https://www.documentcloud.org/documents/6165603-2013-2017AccuracyPUMS.html#document/p18
    ... _American Community Survey's technical documentation
        https://www.documentcloud.org/documents/6165752-2017-SummaryFile-Tech-Doc.html#document/p20/a508561
    ... _the bureau's reference material:
        https://www.census.gov/programs-surveys/acs/technical-documentation/pums/documentation.html
    """
    # Sort the list
    range_list.sort(key=lambda x: x["min"])

    # For each range calculate its min and max value along the universe's scale
    cumulative_n = 0
    for range_ in range_list:
        range_["n_min"] = cumulative_n
        cumulative_n += range_["n"]
        range_["n_max"] = cumulative_n

    # What is the total number of observations in the universe?
    n = sum(d["n"] for d in range_list)

    # What is the estimated midpoint of the n?
    n_midpoint = n / 2.0

    # Now use those to determine which group contains the midpoint.
    n_midpoint_range = next(
        d for d in range_list if n_midpoint >= d["n_min"] and n_midpoint <= d["n_max"]
    )

    # How many households in the midrange are needed to reach the midpoint?
    n_midrange_gap = n_midpoint - n_midpoint_range["n_min"]

    # What is the proportion of the group that would be needed to get the midpoint?
    n_midrange_gap_percent = n_midrange_gap / n_midpoint_range["n"]

    # Apply this proportion to the width of the midrange
    n_midrange_gap_adjusted = (
        n_midpoint_range["max"] - n_midpoint_range["min"]
    ) * n_midrange_gap_percent

    # Estimate the median
    estimated_median = n_midpoint_range["min"] + n_midrange_gap_adjusted

    # If there's no sampling percentage, we can't calculate a margin of error
    if not sampling_percentage:
        # Let's throw a warning, but still return the median
        warnings.warn("", SamplingPercentageWarning)
        return estimated_median, None

    # Get the standard error for this dataset
    standard_error = (
        design_factor
        * math.sqrt(
            ((100 - sampling_percentage) / (n * sampling_percentage)) * (50**2)
        )
    ) / 100

    # Use the standard error to calculate the p values
    p_lower = 0.5 - standard_error
    p_upper = 0.5 + standard_error

    # Estimate the p_lower and p_upper n values
    p_lower_n = n * p_lower
    p_upper_n = n * p_upper

    # Find the ranges the p values fall within
    try:
        p_lower_range_i, p_lower_range = next(
            (i, d)
            for i, d in enumerate(range_list)
            if p_lower_n >= d["n_min"] and p_lower_n <= d["n_max"]
        )
    except StopIteration:
        raise DataError(
            f"The n's lower p value {p_lower_n} does not fall within a data range."
        )

    try:
        p_upper_range_i, p_upper_range = next(
            (i, d)
            for i, d in enumerate(range_list)
            if p_upper_n >= d["n_min"] and p_upper_n <= d["n_max"]
        )
    except StopIteration:
        raise DataError(
            f"The n's upper p value {p_upper_n} does not fall within a data range."
        )

    # Use these values to estimate the lower bound of the confidence interval
    p_lower_a1 = p_lower_range["min"]
    try:
        p_lower_a2 = range_list[p_lower_range_i + 1]["min"]
    except IndexError:
        p_lower_a2 = p_lower_range["max"]
    p_lower_c1 = p_lower_range["n_min"] / n
    try:
        p_lower_c2 = range_list[p_lower_range_i + 1]["n_min"] / n
    except IndexError:
        p_lower_c2 = p_lower_range["n_max"] / n
    lower_bound = ((p_lower - p_lower_c1) / (p_lower_c2 - p_lower_c1)) * (
        p_lower_a2 - p_lower_a1
    ) + p_lower_a1

    # Same for the upper bound
    p_upper_a1 = p_upper_range["min"]
    try:
        p_upper_a2 = range_list[p_upper_range_i + 1]["min"]
    except IndexError:
        p_upper_a2 = p_upper_range["max"]
    p_upper_c1 = p_upper_range["n_min"] / n
    try:
        p_upper_c2 = range_list[p_upper_range_i + 1]["n_min"] / n
    except IndexError:
        p_upper_c2 = p_upper_range["n_max"] / n
    upper_bound = ((p_upper - p_upper_c1) / (p_upper_c2 - p_upper_c1)) * (
        p_upper_a2 - p_upper_a1
    ) + p_upper_a1

    # Calculate the standard error of the median
    standard_error_median = 0.5 * (upper_bound - lower_bound)

    # Calculate the margin of error at the 90% confidence level
    margin_of_error = 1.645 * standard_error_median

    # Return the result
    return estimated_median, margin_of_error


def approximate_proportion(numerator_pair, denominator_pair):
    """Calculate an estimate's proportion of another estimate and approximate the margin of error.

    Follows the U.S. Census Bureau's `official guidelines`_.

    Intended for case where the numerator is a subset of the denominator.
    The `approximate_ratio` method should be used in cases where the
    denominator is larger.

    Args:
        numerator (list): a two-item sequence with a U.S. Census
            bureau estimate and its margin of error.

        denominator (list): a two-item sequence with a U.S. Census
            bureau estimate and its margin of error.

    Returns:
        A two-item sequence containing with the proportion followed by its estimated
        margin of error.

        (0.322, 0.008)

    Examples:
        The percentage of single women in suburban Virginia.

        >>> approximate_proportion((203119, 5070), (690746, 831))
        (0.322, 0.008)

    ... _official guidelines:
        https://www.documentcloud.org/documents/6177941-Acs-General-Handbook-2018-ch08.html#document/p5
    """
    # Pull out the values
    numerator_estimate, numerator_moe = numerator_pair
    denominator_estimate, denominator_moe = denominator_pair

    # Approximate the proportion
    proportion_estimate = numerator_estimate / denominator_estimate

    # Approximate the margin of error
    squared_proportion_moe = numerator_moe**2 - (
        proportion_estimate**2 * denominator_moe**2
    )
    # Ensure it is greater than zero
    if squared_proportion_moe < 0:
        raise DataError(
            "The margin of error is less than zero. Census experts advise using the approximate_ratio method instead."
        )
    proportion_moe = (1.0 / denominator_estimate) * math.sqrt(squared_proportion_moe)

    # Return the result
    return proportion_estimate, proportion_moe


def approximate_ratio(numerator_pair, denominator_pair):
    """Calculate the ratio between two estimates and approximate its margin of error.

    Follows the U.S. Census Bureau's `official guidelines`_.

    Args:
        numerator (list): a two-item sequence with a U.S. Census
            bureau estimate and its margin of error.

        denominator (list): a two-item sequence with a U.S. Census
            bureau estimate and its margin of error.

    Returns:
        A two-item sequence containing the ratio and its approximated margin of error.

        (0.9869791666666666, 0.07170047425884142)

    Examples:
        >>> approximate_ratio((226840, 5556), (203119, 5070))
        (1.117, 0.039)

    ... _official guidelines:
        https://www.documentcloud.org/documents/6177941-Acs-General-Handbook-2018-ch08.html#document/p7
    """
    # Pull out the values
    numerator_estimate, numerator_moe = numerator_pair
    denominator_estimate, denominator_moe = denominator_pair

    # Approximate the ratio
    ratio_estimate = numerator_estimate / denominator_estimate

    # Approximate the margin of error
    squared_ratio_moe = numerator_moe**2 + (
        ratio_estimate**2 * denominator_moe**2
    )
    ratio_moe = (1.0 / denominator_estimate) * math.sqrt(squared_ratio_moe)

    # Return the result
    return ratio_estimate, ratio_moe


def approximate_product(pair_one, pair_two):
    """Calculates the product of two estimates and approximates its margin of error.

    Follows the U.S. Census Bureau's `official guidelines`_.

    Args:
        pair_one (list): a two-item sequence with a U.S. Census
            bureau estimate and its margin of error.

        pair_two (list): a two-item sequence with a U.S. Census
            bureau estimate and its margin of error.

    Returns:
        A two-item sequence containing the estimate and its approximate margin of error.

        (61393366, 202289)

    Examples:
        >>> approximate_product((74506512, 228238), (0.824, 0.001))
        (61393366, 202289)

    ... _official guidelines:
        https://www.documentcloud.org/documents/6177941-Acs-General-Handbook-2018-ch08.html#document/p8
    """
    # Pull out the values
    estimate_one, moe_one = pair_one
    estimate_two, moe_two = pair_two

    # Approximate the product
    product_estimate = estimate_one * estimate_two

    # Approximate the margin of error
    squared_product_moe = (estimate_one**2 * moe_two**2) + (
        estimate_two**2 * moe_one**2
    )
    product_moe = math.sqrt(squared_product_moe)

    # Return the results
    return product_estimate, product_moe


def approximate_percentchange(pair_old, pair_new):
    """Calculates the percent change between two estimates and approximates its margin of error.

    Multiplies results by 100.

    Follows the U.S. Census Bureau's `official guidelines`_.

    Args:
        pair_old (list): a two-item sequence with an earlier U.S. Census
            bureau estimate and its margin of error.

        pair_new (list): a two-item sequence with a later U.S. Census
            bureau estimate and its margin of error.

    Returns:
        A two-item sequence containing the estimate and its approximate margin of error.

                (61393366, 202289)

    Examples:
        The change of percentage of single women in suburban Virginia,
        taken from the bureau's official example as well as data `gathered elsewhere`_.

        >>> approximate_percentchange((135173, 3860), (139301, 4047))
        (3.0538643072211165, 4.198069852261231)

    ... _official guidelines:
        https://www.documentcloud.org/documents/6177941-Acs-General-Handbook-2018-ch08.html#document/p8
    ... _gathered elsewhere:
        https://www.fairfaxcounty.gov/demographics/sites/demographics/files/assets/acs/acs2017.pdf
    """
    # Pull out the values
    estimate_old, moe_old = pair_old
    estimate_new, moe_new = pair_new

    # Approximate the percent change
    percent_change_estimate = ((estimate_new - estimate_old) / estimate_old) * 100

    # Approximate the margin of error
    percent_change_as_ratio = approximate_ratio(pair_new, pair_old)
    decimal_change_moe = percent_change_as_ratio[1]
    percent_change_moe = 100 * decimal_change_moe

    # Return the results
    return percent_change_estimate, percent_change_moe


def approximate_mean(range_list, simulations=50, pareto=False):
    """Estimate a mean and approximate the margin of error.

    The Census Bureau guidelines do not provide instructions for
    approximating a mean using data from the ACS.

    Instead, we implement our own simulation-based approach.

    Due to the stochastic nature of the simulation approach, you will need to set
    a seed before running this function to ensure replicability.

    Note that this function expects you to submit a lower bound for the smallest
    bin and an upper bound for the largest bin. This is often not available for
    ACS datasets like income. We recommend experimenting with different
    lower and upper bounds to assess its effect on the resulting mean.

    Args:
        range_list (list): A list of dictionaries that divide the full range of data values into continuous categories.
            Each dictionary should have four keys:
                * min (int): The minimum value of the range
                * max (int): The maximum value of the range
                * n (int): The number of people, households or other units in the range
                * moe (float): The margin of error for n
        simulations (int): number of simulations to run, used to estimate margin of error. Defaults to 50.
        pareto (logical): Set True to use the Pareto distribution to simulate values in upper bin.
            Set False to assume a uniform distribution. Pareto is often appropriate for income. Defaults to False.

    Returns:
        A two-item tuple with the mean followed by the approximated margin of error.

        (774578.4565215431, 128.94103705296743)

    Examples:
        Estimating the mean for a range of household incomes.

        >>> income = [
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
            dict(min=200000, max=1000000, n=7465517, moe=42206)
        ]
        >>> approximate_mean(income)
        (98045.44530685373, 194.54892406267754)
        >>> approximate_mean(income, pareto=True)
        (60364.96525340687, 58.60735554621351)
    """
    # Sort the list
    range_list.sort(key=lambda x: x["min"])

    if pareto:  # need shape parameter if using Pareto distribution
        nb1 = range_list[-2]["n"]  # number in second to last bin
        nb = range_list[-1]["n"]  # number in last bin
        lb1 = range_list[-2]["min"]  # lower bound of second to last bin
        lb = range_list[-1]["min"]  # lower bound of last bin
        alpha_hat = (numpy.log(nb1 + nb) - numpy.log(nb)) / (
            numpy.log(lb) - numpy.log(lb1)
        )  # shape parameter for Pareto

    simulation_results = []
    for i in range(simulations):
        simulated_values = []
        simulated_n = []
        # loop through every bin except the last one
        for range_ in range_list[:-1]:
            se = range_["moe"] / 1.645  # convert moe to se
            nn = round(
                numpy.random.normal(range_["n"], se)
            )  # use moe to introduce randomness into number in bin
            nn = int(nn)  # clean it up
            simulated_values.append(
                numpy.random.uniform(range_["min"], range_["max"], size=(1, nn)).sum()
            )  # draw random values within the bin, assume uniform
            simulated_n.append(nn)
        # a special case to handle the last bin
        if pareto:
            last = range_list[-1]
            se = last["moe"] / 1.645  # convert moe to se
            nn = round(
                numpy.random.normal(last["n"], se)
            )  # use moe to introduce randomness into number in bin
            nn = int(nn)  # clean it up
            simulated_values.append(
                numpy.random.pareto(a=alpha_hat, size=(1, nn)).sum()
            )  # draw random values within the bin, assume uniform
            simulated_n.append(nn)
        # use uniform otherwise
        else:
            last = range_list[-1]
            se = last["moe"] / 1.645  # convert moe to se
            nn = round(
                numpy.random.normal(last["n"], se)
            )  # use moe to introduce randomness into number in bin
            nn = int(nn)  # clean it up
            simulated_values.append(
                numpy.random.uniform(last["min"], last["max"], size=(1, nn)).sum()
            )  # draw random values within the bin, assume uniform
            simulated_n.append(nn)
        simulation_results.append(
            sum(simulated_values) / sum(simulated_n)
        )  # calculate mean for replicate

    estimated_mean = numpy.mean(simulation_results)  # calculate overall mean
    moe_right = (
        numpy.quantile(simulation_results, 0.95) - estimated_mean
    )  # go from confidence interval to margin of error
    moe_left = estimated_mean - numpy.quantile(
        simulation_results, 0.05
    )  # go from confidence interval to margin of error
    margin_of_error = max(
        moe_left, moe_right
    )  # if asymmetrical take bigger one, conservative

    # Return the result
    return estimated_mean, margin_of_error
