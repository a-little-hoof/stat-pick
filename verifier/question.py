"""read_question: what the model is told before it chooses anything."""

from .checks import result


def verify_input(value):
    # case is an Enum member, so the only wrong value is one the type already refuses.
    return result(True, f"{value.case.value} is a case")


def verify_output(input_value, output_value, workspace):
    if output_value.case is not input_value.case:
        return result(False, f"the question is for {output_value.case.value}, not {input_value.case.value}")
    if not output_value.question.strip():
        return result(False, "the question must not be blank")
    if not output_value.column.strip():
        return result(False, "the question must name the column it is about")
    if output_value.readings < 1:
        return result(False, f"a column of {output_value.readings} readings cannot be summarised")
    return result(True, f"{output_value.column} holds {output_value.readings} readings")
