"""Checks shared by the tool verifiers. Pure functions of their arguments.

The summaries here are the verifier's own, written out again rather than imported: the verifier
may not import the plugin, and it should not take a tool's word for what a column comes to.
tests/test_tables.py holds the two implementations in step.
"""

import statistics

from contract import Statistic

MOST_READINGS = 10000
# A value is right when it is within this much of the one worked out again, relative to its size.
TOLERANCE = 1e-6


def result(valid, message, *, score=None, **details):
    return {
        "valid": valid,
        "score": float(valid) if score is None else score,
        "message": message,
        "details": details,
    }


def numbers_problem(numbers, label):
    """What is wrong with ``numbers`` as a column of readings, or None."""
    if not numbers:
        return f"{label} holds no readings"
    if len(numbers) > MOST_READINGS:
        return f"{label} holds {len(numbers)} readings, more than the {MOST_READINGS} allowed"
    return None


def summarise(numbers, statistic):
    """``statistic`` worked out over ``numbers``, or None when it is not defined for them."""
    if not numbers:
        return None
    if statistic is Statistic.MEAN:
        return statistics.fmean(numbers)
    if statistic is Statistic.MEDIAN:
        return float(statistics.median(numbers))
    if statistic is Statistic.MODE:
        modes = statistics.multimode(numbers)
        return float(modes[0]) if len(modes) == 1 else None
    if statistic is Statistic.RANGE:
        return float(max(numbers) - min(numbers))
    if statistic is Statistic.SPREAD:
        return statistics.pstdev(numbers)
    if statistic is Statistic.SMALLEST:
        return float(min(numbers))
    if statistic is Statistic.LARGEST:
        return float(max(numbers))
    if statistic is Statistic.TOTAL:
        return float(sum(numbers))
    return None


def close(said, wanted):
    """Whether ``said`` is ``wanted`` to within the tolerance, scaled to how big ``wanted`` is."""
    return abs(said - wanted) <= TOLERANCE * max(1.0, abs(wanted))


def shown(value):
    """A value as it reads in a message, without a trailing .0 on a whole number."""
    return str(int(value)) if float(value).is_integer() else f"{value:.6g}"
