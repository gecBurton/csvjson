import io
import json
from typing import Any, Dict, Iterator, List, Union


def _parse_row(row: str) -> List[Any]:
    return json.loads(f"[{row}]")


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
    if header:
        field_names = _parse_row(file_io.readline())
        if all(isinstance(field_name, dict) for field_name in field_names):
            field_names = [field["field"] for field in field_names]
        elif not all(isinstance(field_name, str) for field_name in field_names):
            raise ValueError(
                "all terms in the header should be strings or json-objects"
            )

        for line in file_io.readlines():
            if not line.strip():
                break

            field_values = _parse_row(line.strip())

            if len(field_values) != len(field_names):
                raise ValueError(
                    "all rows must have the same number of terms as the header"
                )
            yield dict(zip(field_names, field_values))
    else:
        for line in file_io.readlines():
            if not line.strip():
                break
            yield _parse_row(line.strip())
