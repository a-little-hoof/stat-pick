"""summarise: one summary of a column, which must report the summary it was asked for."""

from .checks import result


def verify_input(value):
    if not value.column.strip():
        return result(False, "name the column to summarise")
    return result(True, f"{value.statistic.value} of {value.column.strip()}")


def verify_output(input_value, output_value, workspace):
    if output_value.case is not input_value.case:
        return result(False, f"the summary is for {output_value.case.value}, not {input_value.case.value}")
    if output_value.column != input_value.column.strip():
        return result(False, f"the summary is of {output_value.column}, not the {input_value.column.strip()} asked for")
    if output_value.statistic is not input_value.statistic:
        return result(
            False, f"the summary is the {output_value.statistic.value}, not the {input_value.statistic.value} asked for"
        )
    if output_value.readings < 1:
        return result(False, f"a summary over {output_value.readings} readings is not a summary")
    # The readings themselves never leave the plugin, so this is as far as the check can go here;
    # the task's own check works the answer out again from the reference's copy of them.
    return result(
        True, f"{output_value.statistic.value} of {output_value.column} over {output_value.readings} readings"
    )
