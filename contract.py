"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    READ_QUESTION = "read_question"
    SUMMARISE = "summarise"
    SOLUTION = "solution"


class Task(Enum):
    ANSWER_QUESTION = "answer-question"


class Case(Enum):
    DELIVERY_DELAYS = "delivery-delays"
    CLASS_SIZES = "class-sizes"
    SENSOR_DRIFT = "sensor-drift"
    RAINFALL = "rainfall"


class Statistic(Enum):
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    RANGE = "range"
    SPREAD = "spread"
    SMALLEST = "smallest"
    LARGEST = "largest"
    TOTAL = "total"


CASE = "Which question to answer"
COLUMN = "The column of readings the question is about"
STATISTIC = (
    "Which summary answers the question. mean: the readings added up and divided by how many."
    " median: the middle reading once they are in order. mode: the reading that occurs most often."
    " range: the largest less the smallest. spread: how far the readings sit from their mean, as a"
    " population standard deviation. smallest, largest, total: what they say."
)
VALUE = "What that summary comes to for that column"


@dataclass
class CaseInput(Output):
    case: Annotated[Case, CASE]


@dataclass
class QuestionOutput(Output):
    case: Annotated[Case, "The case this question belongs to"]
    question: Annotated[str, "What is being asked, in words; the readings themselves are not shown"]
    column: Annotated[str, COLUMN]
    readings: Annotated[int, "How many readings the column holds"]


@dataclass
class SummariseInput(Output):
    case: Annotated[Case, CASE]
    column: Annotated[str, COLUMN]
    statistic: Annotated[Statistic, STATISTIC]


@dataclass
class SummariseOutput(Output):
    case: Annotated[Case, "The case the column belongs to"]
    column: Annotated[str, "The column summarised, as given"]
    statistic: Annotated[Statistic, "The summary that was worked out"]
    value: Annotated[float, VALUE]
    readings: Annotated[int, "How many readings went into it"]


@dataclass
class AnswerOutput(Output):
    case: Annotated[Case, "The case answered, as the task gave it"]
    statistic: Annotated[Statistic, "The summary that answers the question"]
    value: Annotated[float, VALUE]


@dataclass
class SolutionOutput(Output):
    case: Annotated[Case, "The case this answers"]
    question: Annotated[str, "What was asked"]
    column: Annotated[str, COLUMN]
    numbers: Annotated[list[float], "Every reading in the column, so the answer can be worked out again"]
    statistic: Annotated[Statistic, "The summary that answers the question"]
    value: Annotated[float, VALUE]


TOOLS = {
    Tool.READ_QUESTION: (CaseInput, QuestionOutput),
    Tool.SUMMARISE: (SummariseInput, SummariseOutput),
    Tool.SOLUTION: (CaseInput, SolutionOutput),
}
TASKS = {
    Task.ANSWER_QUESTION: (CaseInput, AnswerOutput),
}
