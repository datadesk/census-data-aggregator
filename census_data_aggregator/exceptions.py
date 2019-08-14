#! /usr/bin/env python
# -*- coding: utf-8 -*-


class DataError(Exception):
    """
    Raised by the data submitted to the function is invalid.
    """
    pass


class SamplingPercentageWarning(Warning):
    """
    Warns that you have not provided a design factor.
    """
    def __str__(self):
        return """A margin of error cannot be calculated unless you provide a sampling percentage."""


class JamValueWarning(Warning):
    """
    Warns that you have not provided jam values when they are needed.
    """
    def __str__(self):
        return """The median falls in the upper or lower bracket. Provide a jam value for more information."""
