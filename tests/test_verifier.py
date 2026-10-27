from __future__ import annotations

from pathlib import Path

import pytest
from slimconfig import build_output, plain_output

import verifier
from contract import TASKS, TOOLS, Case, CaseInput, SolutionOutput, Statistic, SummariseInput, Task, Tool
from plugin import read_question, solution, summarise
from plugin.tables import TABLES, summarise_numbers

# Worked out from the readings by an independent script before the plugin was written.
ANSWERS = {
    Case.DELIVERY_DELAYS: (Statistic.MEDIAN, 2.0),
    Case.CLASS_SIZES: (Statistic.MODE, 24.0),
    Case.SENSOR_DRIFT: (Statistic.SPREAD, 1.8090680674665818),
    Case.RAINFALL: (Statistic.TOTAL, 61.0),
}


# The verifier gets contract instances, as NanoAgent's sandbox builds them from JSON.
def verify_input(tool: str, value: dict) -> dict:
    return verifier.verify_input(tool, build_output(value, TOOLS[Tool(tool)][0]))


def verify_output(tool: str, input_value: dict, output_value: dict, workspace: Path) -> dict:
    given, made = TOOLS[Tool(tool)]
    return verifier.verify_output(
        tool, build_output(input_value, given), build_output(output_value, made), str(workspace)
    )


def verify_task(task: str, arguments: dict, output: dict, workspace: Path, reference: dict | None = None) -> dict:
    given, made = TASKS[Task(task)]
    pinned = None if reference is None else build_output(reference, SolutionOutput)
    given_value, made_value = build_output(arguments, given), build_output(output, made)
    return verifier.verify_task(task, given_value, made_value, pinned, str(workspace))


def answer(case: Case, workspace: Path) -> dict:
    return plain_output(solution(CaseInput(case=case), workspace))


def submit(case: Case, statistic: Statistic, value: float, workspace: Path, reference: dict | None = None) -> dict:
    reference = answer(case, workspace) if reference is None else reference
    made = {"case": case.value, "statistic": statistic.value, "value": value}
    return verify_task("answer-question", {"case": case.value}, made, workspace, reference)


# --- correct ---------------------------------------------------------------


@pytest.mark.parametrize("case", list(Case))
def test_the_right_summary_and_its_value_answer_every_case(tmp_path: Path, case: Case) -> None:
    statistic, value = ANSWERS[case]
    verdict = submit(case, statistic, value, tmp_path)
    assert verdict["valid"] is True and verdict["score"] == 1.0


@pytest.mark.parametrize("case", list(Case))
def test_the_plugin_agrees_with_the_answers_worked_out_beforehand(tmp_path: Path, case: Case) -> None:
    found = answer(case, tmp_path)
    statistic, value = ANSWERS[case]
    assert found["statistic"] == statistic.value
    assert found["value"] == pytest.approx(value)


def test_a_whole_number_given_as_an_integer_still_passes(tmp_path: Path) -> None:
    # 2 and 2.0 are the same answer; JSON may carry either.
    assert submit(Case.DELIVERY_DELAYS, Statistic.MEDIAN, 2, tmp_path)["valid"] is True


# --- incorrect -------------------------------------------------------------


def test_the_mean_does_not_answer_a_question_about_a_typical_parcel(tmp_path: Path) -> None:
    # The whole point of delivery-delays: the mean is 8.73 because two parcels were stuck for weeks.
    mean = summarise_numbers(TABLES[Case.DELIVERY_DELAYS][3], Statistic.MEAN)
    verdict = submit(Case.DELIVERY_DELAYS, Statistic.MEAN, mean, tmp_path)
    assert verdict["valid"] is False and verdict["score"] == 0.0
    assert verdict["details"] == {"chose": "mean", "answers": "median"}


@pytest.mark.parametrize(
    ("case", "wrong"),
    [
        (Case.CLASS_SIZES, Statistic.MEDIAN),
        (Case.SENSOR_DRIFT, Statistic.RANGE),
        (Case.RAINFALL, Statistic.LARGEST),
    ],
)
def test_a_plausible_but_wrong_summary_scores_zero(tmp_path: Path, case: Case, wrong: Statistic) -> None:
    value = summarise_numbers(TABLES[case][3], wrong)
    verdict = submit(case, wrong, value, tmp_path)
    assert verdict["valid"] is False and verdict["score"] == 0.0


def test_the_submitted_case_must_be_the_one_asked_for(tmp_path: Path) -> None:
    statistic, value = ANSWERS[Case.RAINFALL]
    made = {"case": Case.RAINFALL.value, "statistic": statistic.value, "value": value}
    verdict = verify_task(
        "answer-question", {"case": Case.CLASS_SIZES.value}, made, tmp_path, answer(Case.CLASS_SIZES, tmp_path)
    )
    assert verdict["valid"] is False and "not class-sizes" in verdict["message"]


# --- missing ---------------------------------------------------------------


def test_a_reference_with_no_readings_is_refused(tmp_path: Path) -> None:
    statistic, value = ANSWERS[Case.RAINFALL]
    empty = answer(Case.RAINFALL, tmp_path) | {"numbers": []}
    verdict = submit(Case.RAINFALL, statistic, value, tmp_path, empty)
    assert verdict["valid"] is False and "holds no readings" in verdict["message"]


def test_a_reference_for_another_case_is_refused(tmp_path: Path) -> None:
    statistic, value = ANSWERS[Case.RAINFALL]
    verdict = submit(Case.RAINFALL, statistic, value, tmp_path, answer(Case.CLASS_SIZES, tmp_path))
    assert verdict["valid"] is False and "reference answer is for class-sizes" in verdict["message"]


def test_a_reference_with_a_blank_question_is_refused(tmp_path: Path) -> None:
    statistic, value = ANSWERS[Case.RAINFALL]
    blank = answer(Case.RAINFALL, tmp_path) | {"question": "   "}
    verdict = submit(Case.RAINFALL, statistic, value, tmp_path, blank)
    assert verdict["valid"] is False and "name a question and a column" in verdict["message"]


# --- malformed -------------------------------------------------------------


def test_a_reference_whose_value_is_not_its_summary_is_refused(tmp_path: Path) -> None:
    # The verifier works the summary out again rather than believing the reference.
    statistic, value = ANSWERS[Case.CLASS_SIZES]
    lying = answer(Case.CLASS_SIZES, tmp_path) | {"value": 99.0}
    verdict = submit(Case.CLASS_SIZES, statistic, value, tmp_path, lying)
    assert verdict["valid"] is False and "the readings give 24" in verdict["message"]


def test_a_reference_asking_for_a_mode_that_does_not_exist_is_refused(tmp_path: Path) -> None:
    tied = answer(Case.CLASS_SIZES, tmp_path) | {"numbers": [1.0, 1.0, 2.0, 2.0], "statistic": "mode", "value": 1.0}
    verdict = submit(Case.CLASS_SIZES, Statistic.MODE, 1.0, tmp_path, tied)
    assert verdict["valid"] is False and "has no mode" in verdict["message"]


def test_a_reference_with_too_many_readings_is_refused(tmp_path: Path) -> None:
    huge = answer(Case.RAINFALL, tmp_path) | {"numbers": [1.0] * 10001}
    verdict = submit(Case.RAINFALL, Statistic.TOTAL, 10001.0, tmp_path, huge)
    assert verdict["valid"] is False and "more than the 10000 allowed" in verdict["message"]


# --- boundary --------------------------------------------------------------


def test_the_right_summary_with_a_wrong_value_is_half_an_answer(tmp_path: Path) -> None:
    statistic, value = ANSWERS[Case.SENSOR_DRIFT]
    verdict = submit(Case.SENSOR_DRIFT, statistic, value + 0.5, tmp_path)
    assert verdict["valid"] is False and verdict["score"] == 0.5
    assert "right summary" in verdict["message"]


def test_a_value_rounded_too_far_is_refused(tmp_path: Path) -> None:
    # 1.81 is the spread to three figures, and the check wants it to one part in a million.
    assert submit(Case.SENSOR_DRIFT, Statistic.SPREAD, 1.81, tmp_path)["valid"] is False


def test_a_value_inside_the_tolerance_is_accepted(tmp_path: Path) -> None:
    statistic, value = ANSWERS[Case.SENSOR_DRIFT]
    assert submit(Case.SENSOR_DRIFT, statistic, value + 1e-9, tmp_path)["valid"] is True


def test_the_tolerance_scales_with_how_big_the_value_is(tmp_path: Path) -> None:
    # The same absolute slip of 1e-5 is inside the tolerance for 61 and outside it for 2:
    # values are judged to the same relative closeness, not the same absolute one.
    assert submit(Case.RAINFALL, Statistic.TOTAL, 61.0 + 1e-5, tmp_path)["valid"] is True
    assert submit(Case.DELIVERY_DELAYS, Statistic.MEDIAN, 2.0 + 1e-5, tmp_path)["valid"] is False
    assert submit(Case.RAINFALL, Statistic.TOTAL, 61.0 + 1e-3, tmp_path)["valid"] is False


# --- the tools' own checks -------------------------------------------------


@pytest.mark.parametrize("case", list(Case))
def test_read_question_and_solution_agree_on_the_column(tmp_path: Path, case: Case) -> None:
    given = {"case": case.value}
    asked = plain_output(read_question(CaseInput(case=case), tmp_path))
    found = answer(case, tmp_path)
    assert verify_output("read_question", given, asked, tmp_path)["valid"] is True
    assert verify_output("solution", given, found, tmp_path)["valid"] is True
    assert asked["column"] == found["column"] and asked["readings"] == len(found["numbers"])


@pytest.mark.parametrize(
    ("change", "message"),
    [({"question": " "}, "must not be blank"), ({"column": ""}, "name the column"), ({"readings": 0}, "cannot be")],
)
def test_a_question_that_makes_no_sense_is_refused(tmp_path: Path, change: dict, message: str) -> None:
    given = {"case": Case.RAINFALL.value}
    asked = plain_output(read_question(CaseInput(case=Case.RAINFALL), tmp_path)) | change
    verdict = verify_output("read_question", given, asked, tmp_path)
    assert verdict["valid"] is False and message in verdict["message"]


def largest_rainfall(workspace: Path) -> dict:
    given = SummariseInput(case=Case.RAINFALL, column="rain_mm", statistic=Statistic.LARGEST)
    return plain_output(summarise(given, workspace))


def test_summarise_reports_the_summary_it_was_asked_for(tmp_path: Path) -> None:
    given = {"case": Case.RAINFALL.value, "column": "rain_mm", "statistic": "largest"}
    made = largest_rainfall(tmp_path)
    assert verify_input("summarise", given)["valid"] is True
    assert verify_output("summarise", given, made, tmp_path)["valid"] is True
    assert made["value"] == 31.0


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"statistic": "smallest"}, "not the largest asked for"),
        ({"column": "something_else"}, "not the rain_mm asked for"),
        ({"readings": 0}, "is not a summary"),
    ],
)
def test_a_summary_that_is_not_the_one_asked_for_is_refused(tmp_path: Path, change: dict, message: str) -> None:
    given = {"case": Case.RAINFALL.value, "column": "rain_mm", "statistic": "largest"}
    made = largest_rainfall(tmp_path) | change
    verdict = verify_output("summarise", given, made, tmp_path)
    assert verdict["valid"] is False and message in verdict["message"]


def test_summarise_refuses_a_blank_column() -> None:
    verdict = verify_input("summarise", {"case": Case.RAINFALL.value, "column": "  ", "statistic": "mean"})
    assert verdict["valid"] is False and "name the column" in verdict["message"]


def test_summarise_raises_on_a_column_the_case_does_not_have(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="has no column"):
        summarise(SummariseInput(case=Case.RAINFALL, column="days_late", statistic=Statistic.MEAN), tmp_path)
