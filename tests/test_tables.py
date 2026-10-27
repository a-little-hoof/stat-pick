"""The invariants the design rests on: the two sets of summaries agree, every column has exactly
one mode, and the summary a question asks for does not happen to equal any other summary of the
same column — so a right answer is right for the right reason."""

from __future__ import annotations

import statistics

import pytest

from contract import Case, Statistic
from plugin.tables import TABLES, numbers_of, summarise_numbers
from verifier.checks import close
from verifier.checks import summarise as verifier_summarise


def readings(case: Case) -> list[float]:
    return [float(number) for number in TABLES[case][3]]


def test_every_case_has_a_table() -> None:
    assert set(TABLES) == set(Case)


@pytest.mark.parametrize("case", list(Case))
def test_each_case_names_a_column_a_question_and_a_summary(case: Case) -> None:
    column, question, statistic, numbers = TABLES[case]
    assert column.strip() and question.strip()
    assert isinstance(statistic, Statistic)
    assert numbers


@pytest.mark.parametrize("case", list(Case))
def test_every_column_has_exactly_one_mode(case: Case) -> None:
    # Without this, the mode is undefined and summarise would raise on a perfectly fair question.
    assert len(statistics.multimode(readings(case))) == 1


@pytest.mark.parametrize("case", list(Case))
@pytest.mark.parametrize("statistic", list(Statistic))
def test_the_verifier_and_the_plugin_work_out_the_same_summary(case: Case, statistic: Statistic) -> None:
    # The verifier may not import the plugin, so it writes the summaries out again on purpose.
    numbers = readings(case)
    theirs = verifier_summarise(numbers, statistic)
    assert theirs is not None
    assert close(summarise_numbers(numbers, statistic), theirs)


@pytest.mark.parametrize("case", list(Case))
def test_the_wanted_summary_is_not_equalled_by_any_other(case: Case) -> None:
    # Otherwise a wrong choice could land on the right number and look like understanding.
    numbers = readings(case)
    wanted = TABLES[case][2]
    value = summarise_numbers(numbers, wanted)
    same = [
        other.value
        for other in Statistic
        if other is not wanted and close(summarise_numbers(numbers, other), value)
    ]
    assert same == []


def test_the_skewed_column_really_is_skewed() -> None:
    # delivery-delays only tests anything if the mean and the median are far apart.
    numbers = readings(Case.DELIVERY_DELAYS)
    mean = summarise_numbers(numbers, Statistic.MEAN)
    median = summarise_numbers(numbers, Statistic.MEDIAN)
    assert mean > median * 4


def test_the_drifting_sensor_really_passes_its_calibration() -> None:
    # The question says the sensor passes within 2.0 units, so the spread has to be under 2.0.
    assert summarise_numbers(readings(Case.SENSOR_DRIFT), Statistic.SPREAD) < 2.0


def test_the_mode_is_not_the_most_obvious_answer_for_class_sizes() -> None:
    numbers = readings(Case.CLASS_SIZES)
    assert summarise_numbers(numbers, Statistic.MODE) != summarise_numbers(numbers, Statistic.MEDIAN)


@pytest.mark.parametrize("case", list(Case))
def test_a_column_the_case_does_not_have_raises(case: Case) -> None:
    with pytest.raises(ValueError, match="has no column"):
        numbers_of(case, "not_a_column")


def test_summarising_nothing_raises() -> None:
    with pytest.raises(ValueError, match="no readings"):
        summarise_numbers([], Statistic.MEAN)


def test_a_column_with_tied_modes_raises() -> None:
    with pytest.raises(ValueError, match="no single most common"):
        summarise_numbers([1.0, 1.0, 2.0, 2.0], Statistic.MODE)
