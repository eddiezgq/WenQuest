"""Helper for the programs behind worked examples.

A program computes its numbers and hands them to the book with ``out(name=value, ...)``. The build runs the
program, and every ``{{program.name}}`` placeholder in the text is filled from what it handed over, so the numbers
in the book and the numbers the program computes always come from the same place.

    from bookout import out
    out(x_p=0.12321, y_p=0.18660)

Run on its own (``python3 ex4_1_1.py``) a program just prints its values.
"""
from __future__ import annotations

import json
import os
import sys

_values: dict = {}


def out(**values) -> None:
    for k, v in values.items():
        if hasattr(v, "tolist"):          # numpy scalars and arrays
            v = v.tolist()
        _values[k] = v
    path = os.environ.get("WQ_BOOK_OUT")
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_values, f, ensure_ascii=False)
    else:
        for k, v in values.items():
            print(f"{k} = {_values[k]}", file=sys.stdout)
