"""Each case's readings, the question asked of them, and the summary that answers it.

The readings are chosen so that every column has exactly one mode, and so that the summary the
question asks for does not happen to equal any other summary of the same column: a right answer
is right for the right reason.
"""

from __future__ import annotations

import statistics

from contract import Case, Statistic

# case -> (column, question, the summary that answers it, the readings)
TABLES = {
    Case.DELIVERY_DELAYS: (
        "days_late",
        (
            "Nearly every parcel arrives within a few days, but two were stuck for weeks and drag"
            " the average far above what anyone actually waits. How long is a typical parcel delayed?"
        ),
        Statistic.MEDIAN,
        [1, 1, 1, 2, 3, 3, 4, 1, 2, 5, 3, 44, 2, 1, 58],
    ),
    Case.CLASS_SIZES: (
        "students",
        (
            "The registrar orders desks in matching batches and wants one batch size to cover as"
            " many rooms as possible. Which class size occurs most often?"
        ),
        Statistic.MODE,
        [18, 24, 24, 30, 24, 19, 31, 27, 28, 29, 33],
    ),
    Case.SENSOR_DRIFT: (
        "reading",
        (
            "The sensor passes calibration only if its readings sit within 2.0 units of their own"
            " average. How far from the average do the readings sit?"
        ),
        Statistic.SPREAD,
        [50, 52, 48, 51, 49, 53, 47, 50, 52, 48, 50],
    ),
    Case.RAINFALL: (
        "rain_mm",
        (
            "Most days in the month were dry and a few brought storms. The reservoir report needs"
            " how much rain fell over the month altogether. How much was it?"
        ),
        Statistic.TOTAL,
        [0, 0, 0, 2, 0, 0, 14, 0, 0, 0, 31, 0, 0, 5, 0, 0, 0, 0, 9, 0],
    ),
}


def summarise_numbers(numbers: list[float], statistic: Statistic) -> float:
    """``statistic`` worked out over ``numbers``; raises when it is not defined for them."""
    if not numbers:
        raise ValueError("there are no readings to summarise")
    if statistic is Statistic.MEAN:
        return statistics.fmean(numbers)
    if statistic is Statistic.MEDIAN:
        return float(statistics.median(numbers))
    if statistic is Statistic.MODE:
        modes = statistics.multimode(numbers)
        if len(modes) != 1:
            raise ValueError(f"no single most common reading: {sorted(modes)} all occur as often")
        return float(modes[0])
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
    raise ValueError(f"no such summary: {statistic}")


def numbers_of(case: Case, column: str) -> list[float]:
    """``case``'s readings for ``column``; raises when the case has no such column."""
    named, _, _, numbers = TABLES[case]
    if column != named:
        raise ValueError(f"the {case.value} case has no column {column!r}, only {named!r}")
    return [float(number) for number in numbers]
