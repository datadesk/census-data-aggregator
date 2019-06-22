import math


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


def approximate_median(range_list):
    """
    Returns the estimated median from a set of ranged totals.

    Useful for generated medians for measures like median household income and median agn when aggregating census geographies.

    Expects a list of dictionaries with three keys:

        min: The minimum value in the range
        max: The maximum value in the range
        n: The number of people, households or other universe figure in the range
    """
    # Sort the list
    range_list.sort(key=lambda x: x['start'])

    # What is the total number of observations in the universe?
    n = sum([d['total'] for d in range_list])

    # What is the midpoint of the universe?
    midpoint = n / 2.0

    # For each range calculate its min and max value along the universe's scale
    running_total = 0
    for range_ in range_list:
        range_['n_min'] = running_total
        range_['n_max'] = running_total + range_['total']
        running_total += range_['total']

    # Now use those to determine which group contains the midpoint.
    try:
        midpoint_range = next(d for d in range_ if midpoint >= d['n_min'] and mindpoint <= d['n_max'])
    except StopIteration:
        raise StopIteration("The midpoint of the total does not fall within a data range.")

    # How many households in the midrange are needed to reach the midpoint?
    midrange_gap = midpoint - midpoint_range['n_min']

    # What is the proportion of the group that would be needed to get the midpoint?
    midrange_gap_percent = midrange_gap / midpoint_range['total']

    # Apply this proportion to the width of the midrange
    midrange_gap_adjusted = (range_['end'] - range_['start']) * midrange_gap_percent

    # Estimate the median
    estimated_median = range_['start'] + midrange_gap_adjusted

    # Return the result
    return estimated_median
