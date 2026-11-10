#!/usr/bin/env python3
"""Lesson 1 numbers: a toy next-token distribution for
"The ultimate tensile strength of 6061-T6 aluminum is about ___".

The same LOGITS are embedded in src/en/labs/nexttoken.html (check: tools/check_ch01.py).
Correct answers for UTS: 310 MPa / 45 ksi (ASM typical values; 276 MPa / 40 ksi is the YIELD strength).
"""
import json
import math
import os

LOGITS = {"310 MPa": 2.2, "45 ksi": 1.6, "276 MPa": 1.9, "290 MPa": 1.0, "40 ksi": 1.1, "350 MPa": 0.4}
CORRECT = {"310 MPa", "45 ksi"}
TEMPS = {"t02": 0.2, "t07": 0.7, "t10": 1.0, "t15": 1.5}


def probs(t):
    z = {k: math.exp(v / t) for k, v in LOGITS.items()}
    s = sum(z.values())
    return {k: v / s for k, v in z.items()}


def main():
    out = {}
    for key, t in TEMPS.items():
        p = probs(t)
        out[f"ok_{key}"] = 100 * sum(p[k] for k in CORRECT)
        out[f"wrong_{key}"] = 100 - out[f"ok_{key}"]
        out[f"yield_{key}"] = 100 * p["276 MPa"]
    out["one_in"] = round(100 / out["wrong_t02"])     # "about 1 in N answers is wrong" at T = 0.2
    # Lab 1-3: a 6 mm x 25 mm bar in tension, with the wrong (yield) and the right (UTS) strength
    out["area"] = 6 * 25                                 # mm^2
    out["f_yield"] = out["area"] * 276                   # N (what the AI wrote)
    out["f_uts"] = out["area"] * 310                     # N (with the handbook UTS)
    path = os.environ.get("WQ_BOOK_OUT")
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f)
    else:
        print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
