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


# ---------------------------------------------------------------- figures (示意图)

COLORS = {"x": "#d62728", "y": "#2ca02c", "z": "#1f77b4", "ink": "#1d2327", "muted": "#7a868d", "accent": "#b8860b"}


def style():
    """The book's figure style: Chinese labels in Noto Sans CJK, thin lines, x red / y green / z blue."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": ["Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans"], "mathtext.fontset": "cm", "font.size": 11,
        "axes.unicode_minus": False, "svg.fonttype": "path", "figure.dpi": 100,
    })
    return plt


def figure(fig, name: str) -> None:
    """Save a static figure for the book as <name>.svg; the text shows it with ``::: 图 x.y.z`` / ``src: name``."""
    folder = os.environ.get("WQ_BOOK_FIGDIR")
    path = os.path.join(folder, f"{name}.svg") if folder else f"{name}.svg"
    fig.savefig(path, format="svg", bbox_inches="tight", pad_inches=0.05, transparent=True)
    if not folder:
        print(f"figure saved: {path}")
    _values.setdefault("_figures", []).append(name)
    out()


# ---------------------------------------------------------------- matrices for the text

def num(x: float, digits: int = 4) -> str:
    """A number as printed in the book: fixed decimals, exact integers without decimals, no "-0"."""
    if abs(x - round(x)) < 1e-12:
        return str(int(round(x)))
    s = f"{x:.{digits}f}"
    return "0" if float(s) == 0 else s


def tex(M, digits: int = 4, env: str = "pmatrix") -> str:
    """A matrix or column vector as LaTeX, e.g. out(R=tex(R)) and {{ex.R}} inside $$...$$."""
    import numpy as np
    A = np.atleast_2d(np.asarray(M, dtype=float))
    if A.shape[0] == 1 and np.asarray(M).ndim == 1:
        A = A.T
    rows = [" & ".join(num(v, digits) for v in row) for row in A]
    return f"\\begin{{{env}}} " + r" \\ ".join(rows) + f" \\end{{{env}}}"


def vec(v, digits: int = 4) -> str:
    """A column vector written on one line, (a, b, c)^T, for use inside running text."""
    return "(" + ",\\ ".join(num(float(x), digits) for x in v) + ")^{\\mathsf T}"
