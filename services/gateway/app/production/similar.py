"""相似度检查 (team rebuild R3): is an AI-written animation or lab a copy of an example or of another lesson?

The code is cut into tokens (names, numbers, strings — the words inside strings count, so copied captions and
titles count); runs of 6 tokens are compared. The share of this code's runs that also appear in one reference
is how much of it was copied from that reference. Code written with the same parts but for a different lesson
shares little beyond the API calls themselves, which are short.
"""
from __future__ import annotations

import re

N = 6
LIMIT = 0.4        # at least this share of runs found in one reference = a copy
PLACEHOLDER = re.compile(r"（占位）|\(placeholder\)|\bX\.Y\b|占位内容")

_TOKEN = re.compile(r"[A-Za-z_][A-Za-z_0-9]*|\d+(?:\.\d+)?|[一-鿿]|[^\s\w]")


def tokens(code: str) -> list[str]:
    code = re.sub(r"(?m)^\s*(#|//).*$", "", code or "")   # comments do not count
    return _TOKEN.findall(code)


def runs(code: str) -> set[tuple[str, ...]]:
    t = tokens(code)
    return {tuple(t[i:i + N]) for i in range(max(0, len(t) - N + 1))}


def copied(code: str, refs: dict[str, str]) -> tuple[str, float] | None:
    """(reference name, share) of the reference this code copies most, when that share reaches LIMIT."""
    mine = runs(code)
    if not mine:
        return None
    best = ("", 0.0)
    for name, ref in refs.items():
        if not ref:
            continue
        share = len(mine & runs(ref)) / len(mine)
        if share > best[1]:
            best = (name, share)
    return best if best[1] >= LIMIT else None


def problem(code: str, refs: dict[str, str]) -> str:
    """The message for the author ('' when the code is its own)."""
    if PLACEHOLDER.search(code or ""):
        return ("the code still contains the example's placeholder text (（占位）/placeholder/X.Y); "
                "write THIS lesson's own titles, captions and numbers")
    hit = copied(code, refs)
    if hit:
        return (f"about {round(hit[1] * 100)}% of the code is the same as {hit[0]}; do not reuse it — "
                "design THIS lesson's own picture, motion, numbers and texts from the lesson spec and the course design book")
    return ""
