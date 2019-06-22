#! /usr/bin/env python
# -*- coding: utf-8 -*-
import math
import warnings
from .exceptions import DesignFactorWarning


def approximate_sum(*pairs):
    """
    Returns the combined value of all the provided Census Bureau estimates, along with an approximated margin of error.

    Expects a series of arguments, each a paired list with the estimated value first and the margin of error second.
    """
    # According to the Census Bureau, when approximating a sum use only the largest zero estimate margin of error, once
    # https://www.documentcloud.org/documents/6162551-20180418-MOE.html#document/p52
    zeros = [p for p in pairs if p[0] == 0]
    # So if there are zeros...
    if len(zeros) > 1:
        # ... weed them out
        max_zero_margin = max([p[1] for p in zeros])
        not_zero_margins = [p[1] for p in pairs if p[0] != 0]
        margins = [max_zero_margin] + not_zero_margins
    # If not, just keep all the input margins
    else:
        margins = [p[1] for p in pairs]

    # Calculate the margin using the bureau's official formula
    margin_of_error = math.sqrt(sum([m**2 for m in margins]))

    # Calculate the total
    total = sum([p[0] for p in pairs])

    # Return the results
    return total, margin_of_error


def approximate_median(range_list, design_factor=None):
    """
    Returns the estimated median from a set of ranged totals, along with an approximated margin of error.

    Useful for generating medians for measures like household income and age when aggregating census geographies.

    Expects a list of dictionaries with three keys:

        min: The minimum value in the range
        max: The maximum value in the range
        n: The number of people, households or other universe figure in the range

    For a margin of error to be returned, a "design factor" must be provided to calculate the standard errorself.

    Design factors for different census surveys and tables can be found in the "PUMS Accuracy" CSV files. https://www.census.gov/programs-surveys/acs/technical-documentation/pums/documentation.html
    """
    # Sort the list
    range_list.sort(key=lambda x: x['min'])

    # For each range calculate its min and max value along the universe's scale
    cumulative_n = 0
    for range_ in range_list:
        range_['n_min'] = cumulative_n
        cumulative_n += range_['n']
        range_['n_max'] = cumulative_n

    # What is the total number of observations in the universe?
    n = sum([d['n'] for d in range_list])

    # What is the estimated midpoint of the n?
    n_midpoint = n / 2.0

    # Now use those to determine which group contains the midpoint.
    try:
        n_midpoint_range = next(d for d in range_list if n_midpoint >= d['n_min'] and n_midpoint <= d['n_max'])
    except StopIteration:
        raise StopIteration("The n's midpoint does not fall within a data range.")

    # How many households in the midrange are needed to reach the midpoint?
    n_midrange_gap = n_midpoint - n_midpoint_range['n_min']

    # What is the proportion of the group that would be needed to get the midpoint?
    n_midrange_gap_percent = n_midrange_gap / n_midpoint_range['n']

    # Apply this proportion to the width of the midrange
    n_midrange_gap_adjusted = (n_midpoint_range['max'] - n_midpoint_range['min']) * n_midrange_gap_percent

    # Estimate the median
    estimated_median = n_midpoint_range['min'] + n_midrange_gap_adjusted

    # If there's no design factor, we can't calculate a margin of error
    if not design_factor:
        # Let's throw a warning, but still return the median
        warnings.warn("", DesignFactorWarning)
        return estimated_median, None

    # Get the standard error for this dataset
    standard_error = (design_factor * math.sqrt((99/n)*(50**2))) / 100

    # Use the standard error to calculate the p values
    p_lower = (.5 - standard_error)
    p_upper = (.5 + standard_error)

    # Estimate the p_lower and p_upper n values
    p_lower_n = n * p_lower
    p_upper_n = n * p_upper

    # Find the ranges the p values fall within
    try:
        p_lower_range_i, p_lower_range = next(
            (i, d) for i, d in enumerate(range_list)
                if p_lower_n >= d['n_min'] and p_lower_n <= d['n_max']
        )
    except StopIteration:
        raise StopIteration("The n's lower p value does not fall within a data range.")

    try:
        p_upper_range_i, p_upper_range = next(
            (i, d) for i, d in enumerate(range_list)
                if p_upper_n >= d['n_min'] and p_upper_n <= d['n_max']
        )
    except StopIteration:
        raise StopIteration("The n's higher p value does not fall within a data range.")

    # Use these values to estimate the lower bound of the confidence interval
    p_lower_a1 = p_lower_range['min']
    try:
        p_lower_a2 = range_list[p_lower_range_i+1]['min']
    except IndexError:
        p_lower_a2 = p_lower_range['max']
    p_lower_c1 = p_lower_range['n_min'] / n
    try:
        p_lower_c2 = range_list[p_lower_range_i+1]['n_min'] / n
    except IndexError:
        p_lower_c2 = p_lower_range['n_max'] / n
    lower_bound = ((p_lower - p_lower_c1) / (p_lower_c2 - p_lower_c1)) * (p_lower_a2 - p_lower_a1) + p_lower_a1

    # Same for the upper bound
    p_upper_a1 = p_upper_range['min']
    try:
        p_upper_a2 = range_list[p_upper_range_i+1]['min']
    except IndexError:
        p_upper_a2 = p_upper_range['max']
    p_upper_c1 = p_upper_range['n_min'] / n
    try:
        p_upper_c2 = range_list[p_upper_range_i+1]['n_min'] / n
    except IndexError:
        p_upper_c2 = p_upper_range['n_max'] / n
    upper_bound = ((p_upper - p_upper_c1) / (p_upper_c2 - p_upper_c1)) * (p_upper_a2 - p_upper_a1) + p_upper_a1

    # Calculate the standard error of the median
    standard_error_median = 0.5 * (upper_bound - lower_bound)

    # Calculate the margin of error at the 90% confidence level
    margin_of_error = 1.645 * standard_error_median

    # Return the result
    return estimated_median, margin_of_error
