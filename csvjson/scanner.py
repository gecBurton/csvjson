"""JSON token scanner
follows json.scanner.py
"""
import json


def csv_make_scanner(context):
    parse_object = context.parse_object
    parse_array = context.parse_array
    parse_string = context.parse_string
    match_number = json.scanner.NUMBER_RE.match
    strict = context.strict
    parse_float = context.parse_float
    parse_int = context.parse_int
    parse_constant = context.parse_constant
    object_hook = context.object_hook
    object_pairs_hook = context.object_pairs_hook
    memo = context.memo

    def _scan_once(string, idx):
        try:
            next_char = string[idx]
        except IndexError:
            raise StopIteration(idx) from None

        if next_char == '"':
            return parse_string(string, idx + 1, strict)
        if next_char == "{":
            return parse_object(
                (string, idx + 1),
                strict,
                _scan_once,
                object_hook,
                object_pairs_hook,
                memo,
            )
        if next_char == "[":
            return parse_array((string, idx + 1), _scan_once)
        if string[idx : idx + 4].lower() == "null":
            return None, idx + 4
        if string[idx : idx + 4].lower() == "true":
            return True, idx + 4
        if string[idx : idx + 5].lower() == "false":
            return False, idx + 5
        if next_char in ",]":
            return None, idx

        number = match_number(string, idx)
        if number is not None:
            integer, fraction, exponent = number.groups()
            if fraction or exponent:
                res = parse_float(integer + (fraction or "") + (exponent or ""))
            else:
                res = parse_int(integer)
            return res, number.end()
        if string[idx : idx + 3] == "NaN":
            return parse_constant("NaN"), idx + 3
        if string[idx : idx + 8] == "Infinity":
            return parse_constant("Infinity"), idx + 8
        if string[idx : idx + 9] == "-Infinity":
            return parse_constant("-Infinity"), idx + 9
        raise StopIteration(idx)

    def scan_once(string, idx):
        try:
            return parse_array((string, idx + 1), _scan_once)
        finally:
            memo.clear()

    return scan_once
