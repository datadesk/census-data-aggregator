#! /usr/bin/env python
# -*- coding: utf-8 -*-


class DataError(Exception):
    """
    Raised by the data submitted to the function is invalid.
    """
    pass


class InputError(Exception):
    """
    Raised if jam value input is invalid.
    """
    pass


class SamplingPercentageWarning(Warning):
    """
    Warns that you have not provided a design factor.
    """
    def __str__(self):
        return """A margin of error cannot be calculated unless you provide a sampling percentage."""


class JamValueMissingWarning(Warning):
    """
    Warns that you have not provided jam values when they are needed.
    """
    def __str__(self):
        return """The median falls in the upper or lower bracket. Provide a jam value for more information."""


class JamValueResultWarning(Warning):
    """
    Warns that the estiamte is a jam value.
    """
    def __str__(self):
        return """The median falls in the upper or lower bracket. A jam value is returned as the median estimate."""


class JamValueResultMOEWarning(Warning):
    """
    Warns that the estiamte is not provided because averaging jam values is inappropriate.
    """
    def __str__(self):
        return """The median falls in the upper or lower bracket. No estimate is returned since an average over jam values is inappropriate."""
