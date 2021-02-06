import math
from json import JSONDecodeError

import pytest

from csvjson.csvjson import CSVJSONDecoder, _parse_row


def test_basic_types():
    assert _parse_row('"a", 4.5, -1, false') == ["a", 4.5, -1, False]


def test_math_nan():
    assert math.isnan(_parse_row("NaN")[0])


def test_math_inf():
    assert math.isinf(_parse_row("Infinity")[0])
    assert math.isinf(_parse_row("-Infinity")[0])


def test_csv_make_scanner_raises_stop_iteration_from_over_running_legitimate_text():
    csv_json_decoder = CSVJSONDecoder()
    with pytest.raises(JSONDecodeError):
        csv_json_decoder.scan_once('[1]', 2)


def test_csv_make_scanner_raises_stop_iteration_from_illegitimate_text():
    csv_json_decoder = CSVJSONDecoder()
    with pytest.raises(JSONDecodeError):
        csv_json_decoder.scan_once('["a]', 1)
