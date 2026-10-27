"""read_question, summarise and solution: the question, one summary of a column, and the answer."""

from __future__ import annotations

from pathlib import Path

from contract import CaseInput, QuestionOutput, SolutionOutput, SummariseInput, SummariseOutput
from plugin.tables import TABLES, numbers_of, summarise_numbers


def read_question(given: CaseInput, workspace: Path) -> QuestionOutput:
    column, question, _, numbers = TABLES[given.case]
    return QuestionOutput(case=given.case, question=question, column=column, readings=len(numbers))


def summarise(given: SummariseInput, workspace: Path) -> SummariseOutput:
    numbers = numbers_of(given.case, given.column.strip())
    return SummariseOutput(
        case=given.case,
        column=given.column.strip(),
        statistic=given.statistic,
        value=summarise_numbers(numbers, given.statistic),
        readings=len(numbers),
    )


def solution(given: CaseInput, workspace: Path) -> SolutionOutput:
    """The task's reference tool: NanoAgent runs it out of the model's sight."""
    column, question, statistic, _ = TABLES[given.case]
    numbers = numbers_of(given.case, column)
    return SolutionOutput(
        case=given.case,
        question=question,
        column=column,
        numbers=numbers,
        statistic=statistic,
        value=summarise_numbers(numbers, statistic),
    )
