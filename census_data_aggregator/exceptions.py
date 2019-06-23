#! /usr/bin/env python
# -*- coding: utf-8 -*-


class DataError(Exception):
    """
    Raised by the data submitted to the function is invalid.
    """
    pass


class DesignFactorWarning(Warning):
    """
    Warns that you have not provided a design factor.
    """
    def __str__(self):
        return """A margin of error cannot be calculated unless you provide a design factor.

Design factors for different census surveys and tables can be found in the "PUMS Accuracy" CSV files. https://www.census.gov/programs-surveys/acs/technical-documentation/pums/documentation.html
"""
