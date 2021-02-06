import io
import json
from typing import Any, Dict, Iterator, List, Union

from csvjson.scanner import csv_make_scanner


class CSVJSONDecoder(json.decoder.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scan_once = csv_make_scanner(self)


def _parse_row(row: str) -> List[Any]:
    return json.loads(f"[{row.strip()}]", cls=CSVJSONDecoder)


def load(
    file_io: io.TextIOWrapper, header: bool = True
) -> Iterator[Union[Dict[str, Any], Any]]:
    """load csv into json following the web+csv format
    https://github.com/DrorHarari/csvjson

    :example:
        >>> csv = '''"name", "age"
        ...          "George, B",38
        ...          "Alice", null
        ...        '''
        >>> list(load(io.StringIO(csv)))
        [{'name': 'George, B', 'age': 38}, {'name': 'Alice', 'age': None}]

    """
    if not header:
        first_row = _parse_row(file_io.readline())
        yield first_row
        for line in file_io.readlines():
            if not line.strip():
                break
            row = _parse_row(line)
            if len(row) != len(first_row):
                raise ValueError(
                    "all rows must have the same number of columns"
                )
            yield row

    field_names = _parse_row(file_io.readline())
    if not all(isinstance(field_name, str) for field_name in field_names):
        raise ValueError(
            "all terms in the header must be strings"
        )

    for line in file_io.readlines():
        if not line.strip():
            break

        field_values = _parse_row(line.strip())

        if len(field_values) != len(field_names):
            raise ValueError(
                "all rows must have the same number of columns"
            )
        yield dict(zip(field_names, field_values))
