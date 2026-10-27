"""solution (the answer-question reference) and the answer-question task's own check.

The answer has two parts, and they are judged separately: choosing which summary answers the
question is the model's whole job, and the value then has to be that summary's. A right choice
with the wrong number is half right, and scores accordingly.
"""

from .checks import close, numbers_problem, result, shown, summarise

CHOICE_ONLY = 0.5


def verify_input(value):
    return result(True, f"{value.case.value} is a case")


def _answer_problem(value, label):
    """What is wrong with a question-and-answer, or None."""
    problem = numbers_problem(value.numbers, f"{label} column")
    if problem:
        return problem
    if not value.question.strip() or not value.column.strip():
        return f"{label} answer must name a question and a column"
    worked = summarise(value.numbers, value.statistic)
    if worked is None:
        return f"{label} column has no {value.statistic.value}"
    if not close(value.value, worked):
        return f"{label} {value.statistic.value} is {shown(value.value)}, but the readings give {shown(worked)}"
    return None


def verify_output(input_value, output_value, workspace):
    if output_value.case is not input_value.case:
        return result(False, f"the answer is for {output_value.case.value}, not {input_value.case.value}")
    problem = _answer_problem(output_value, "the answer's")
    if problem:
        return result(False, problem)
    return result(True, f"{output_value.case.value} is answered by the {output_value.statistic.value}")


def verify_task(arguments, output, reference, workspace):
    """answer-question: the chosen summary and its value judged against the answer the model never saw."""
    if output.case is not arguments.case:
        return result(False, f"the answer is for {output.case.value}, not {arguments.case.value}")
    if reference.case is not arguments.case:
        return result(False, f"the reference answer is for {reference.case.value}, not {arguments.case.value}")
    # The verifier does not take the reference tool's word for it either.
    problem = _answer_problem(reference, "the reference")
    if problem:
        return result(False, problem)
    if output.statistic is not reference.statistic:
        return result(
            False,
            f"the {output.statistic.value} does not answer the question; the {reference.statistic.value} does",
            score=0.0,
            chose=output.statistic.value,
            answers=reference.statistic.value,
        )
    # Right choice: the value now has to be that summary's, worked out from the readings again.
    worked = summarise(reference.numbers, output.statistic)
    if not close(output.value, worked):
        return result(
            False,
            f"the {output.statistic.value} is the right summary, but it comes to"
            f" {shown(worked)}, not the {shown(output.value)} given",
            score=CHOICE_ONLY,
            worked_out=worked,
        )
    return result(
        True,
        f"the {output.statistic.value} answers the question, and it is {shown(worked)}",
        readings=len(reference.numbers),
    )
