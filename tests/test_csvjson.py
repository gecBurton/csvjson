#!/usr/bin/env python

"""Tests for `csvjson` package."""
import io

import pytest

from csvjson.csvjson import load


def test_regular_CSV():
    """https://github.com/DrorHarari/csvjson#regular-csv
    """
    csv = r"""1,"John","12 Totem Rd. Aspen",true
    2,"Bob",null,false
    3,"Sue","Bigsby, 345 Carnival, WA 23009",false
    """
    expected = [
        [1, "John", "12 Totem Rd. Aspen", True],
        [2, "Bob", None, False],
        [3, "Sue", "Bigsby, 345 Carnival, WA 23009", False],
    ]
    assert list(load(io.StringIO(csv), header=False)) == expected


def test_CSV_with_headers_row():
    """https://github.com/DrorHarari/csvjson#csv-with-headers-row
    """

    csv = r""""id","name","address","regular"
    1,"John","12 Totem Rd. Aspen",true
    2,"Bob",null,false
    3,"Sue","Bigsby, 345 Carnival, WA 23009",false
    """
    expected = [
        {"address": "12 Totem Rd. Aspen", "id": 1, "name": "John", "regular": True},
        {"address": None, "id": 2, "name": "Bob", "regular": False},
        {
            "address": "Bigsby, 345 Carnival, WA 23009",
            "id": 3,
            "name": "Sue",
            "regular": False,
        },
    ]
    assert list(load(io.StringIO(csv))) == expected


def test_CSV_with_data_containing_quotes_and_commas():
    """https://github.com/DrorHarari/csvjson#csv-with-data-containing-quotes-and-commas
    """

    csv = r""""id","name","address","regular"
    1,"John","12 Totem Rd., Aspen",true
    2,"Bob",null,false
    3,"Sue","\"Bigsby\", 345 Carnival, WA 23009",false
    """
    expected = [
        {"address": "12 Totem Rd., Aspen", "id": 1, "name": "John", "regular": True},
        {"address": None, "id": 2, "name": "Bob", "regular": False},
        {
            "address": '"Bigsby", 345 Carnival, WA 23009',
            "id": 3,
            "name": "Sue",
            "regular": False,
        },
    ]
    assert list(load(io.StringIO(csv))) == expected


def test_CSV_with_complex_headers():
    """https://github.com/DrorHarari/csvjson#csv-with-complex-headers
    """

    csv = r"""{"field":"id","type":"int"},{"field":"name","type":"string"},{"field":"address","type":"string"},{"field":"regular","type":"boolean"}
    1,"John","12 Totem Rd. Aspen",true
    2,"Bob",null,false
    3,"Sue","Bigsby, 345 Carnival, WA 23009",false
    """

    expected = [
        {"address": "12 Totem Rd. Aspen", "id": 1, "name": "John", "regular": True},
        {"address": None, "id": 2, "name": "Bob", "regular": False},
        {
            "address": "Bigsby, 345 Carnival, WA 23009",
            "id": 3,
            "name": "Sue",
            "regular": False,
        },
    ]
    assert list(load(io.StringIO(csv))) == expected


def test_CSV_with_array_data():
    """https://github.com/DrorHarari/csvjson#csv-with-array-data
    """

    csv = r"""1,"directions",["north","south","east","west"]
    2,"colors",["red","green","blue"]
    3,"drinks",["soda","water","tea","coffe"]
    4,"spells",[]
    """
    expected = [
        [1, "directions", ["north", "south", "east", "west"]],
        [2, "colors", ["red", "green", "blue"]],
        [3, "drinks", ["soda", "water", "tea", "coffe"]],
        [4, "spells", []],
    ]
    with pytest.raises(ValueError) as error:
        list(load(io.StringIO(csv), header=False))
    assert str(error.value) == "array values not allowed"
    assert list(load(io.StringIO(csv), header=False, objects=True)) == expected


def test_CSV_with_all_kinds_of_data():
    """https://github.com/DrorHarari/csvjson#csv-with-all-kinds-of-data
    """

    csv = r""""index","value1","value2"
    "number",1,2
    "boolean",false,true
    "null",null,"non null"
    "array of numbers",[1],[1,2]
    "simple object",{"a": 1},{"a":1, "b":2}
    "array with mixed objects",[1,null,"ball"],[2,{"a": 10, "b": 20},"cube"]
    "string with quotes","a\"b","alert(\"Hi!\")"
    "string with bell&newlines","bell is \u0007","multi\nline\ntext"
    """
    expected = [
        {"index": "number", "value1": 1, "value2": 2},
        {"index": "boolean", "value1": False, "value2": True},
        {"index": "null", "value1": None, "value2": "non null"},
        {"index": "array of numbers", "value1": [1], "value2": [1, 2]},
        {"index": "simple object", "value1": {"a": 1}, "value2": {"a": 1, "b": 2}},
        {
            "index": "array with mixed objects",
            "value1": [1, None, "ball"],
            "value2": [2, {"a": 10, "b": 20}, "cube"],
        },
        {"index": "string with quotes", "value1": 'a"b', "value2": 'alert("Hi!")'},
        {
            "index": "string with bell&newlines",
            "value1": "bell is \x07",
            "value2": "multi\nline\ntext",
        },
    ]
    with pytest.raises(ValueError) as error:
        list(load(io.StringIO(csv), header=False))
    assert str(error.value) == "array values not allowed"
    assert list(load(io.StringIO(csv), objects=True)) == expected


def test_incorrect_headers():
    csv = r""""index","value1",2
    "number",1,2"""

    with pytest.raises(ValueError) as error:
        list(load(io.StringIO(csv)))
    assert (
        str(error.value) == "all terms in the header should be strings or json-objects"
    )


def test_different_row_lengths():
    csv = r""""index","value1","value2"
    "number",1"""

    with pytest.raises(ValueError) as error:
        list(load(io.StringIO(csv)))
    assert (
        str(error.value) == "all rows must have the same number of terms as the header"
    )
