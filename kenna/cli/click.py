from typing import Any, List
from click import *
from kenna.cli.constants import HIDE_RISK_METER_SCORES_BY_DEFAULT, HIDE_COUNTS_BY_DEFAULT, HIDE_EMPTY_VALUES_BY_DEFAULT

import hodgepodge.click
import json
import copy


_echo = copy.copy(echo)


def echo(
        data: Any,
        hide_risk_meter_scores: bool = HIDE_RISK_METER_SCORES_BY_DEFAULT,
        hide_counts: bool = HIDE_COUNTS_BY_DEFAULT,
        hide_empty_values: bool = HIDE_EMPTY_VALUES_BY_DEFAULT):

    if isinstance(data, dict):

        #: Optionally remove current and historical risk meter scores.
        if hide_risk_meter_scores:
            data = dict((k, v) for (k, v) in data.items() if 'score' not in k)

        #: Optionally remove current and historical counts.
        if hide_counts:
            data = dict((k, v) for (k, v) in data.items() if 'count' not in k)

        #: Optionally hide empty values.
        if hide_empty_values:
            data = dict((k, v) for (k, v) in data.items() if v or isinstance(v, (int, float)))

        data = json.dumps(data)
    _echo(data)


def str_to_strs(data: str) -> List[str]:
    return hodgepodge.click.str_to_strs(data)


def str_to_ints(data: str) -> List[int]:
    return hodgepodge.click.str_to_ints(data)
