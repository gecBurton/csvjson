import math

import pytest

from csvjson.csvjson import CSVJSONDecoder, _parse_simple_row


def test_basic_types():
    assert _parse_simple_row('"a", 4.5, -1, false') == ["a", 4.5, -1, False]


def test_math_nan():
    assert math.isnan(_parse_simple_row("NaN")[0])


def test_math_inf():
    assert math.isinf(_parse_simple_row("Infinity")[0])
    assert math.isinf(_parse_simple_row("-Infinity")[0])


def test_object():
    with pytest.raises(ValueError) as error:
        _parse_simple_row('{"a": 1}')
    assert str(error.value) == "object values not allowed"


def test_array():
    with pytest.raises(ValueError) as error:
        _parse_simple_row('["a"]')
    assert str(error.value) == "array values not allowed"


def test_csv_make_scanner_raises_stop_iteration_from_over_running_legitimate_text():
    csv_json_decoder = CSVJSONDecoder()
    with pytest.raises(StopIteration):
        csv_json_decoder.scan_once('["1"]', 4)


def test_csv_make_scanner_raises_stop_iteration_from_illegitimate_text():
    csv_json_decoder = CSVJSONDecoder()
    with pytest.raises(StopIteration):
        csv_json_decoder.scan_once('["a"]', 1)
