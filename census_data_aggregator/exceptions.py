class DataError(Exception):
    """Raised by the data submitted to the function is invalid."""

    pass


class SamplingPercentageWarning(Warning):
    """Warns that you have not provided a design factor."""

    def __str__(self):
        return """A margin of error cannot be calculated unless you provide a sampling percentage."""
