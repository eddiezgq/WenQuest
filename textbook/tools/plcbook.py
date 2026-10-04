"""PLC programs in the book (《PLC 原理及实践》, 第 18 轮): run them on the platform's PLC engine and virtual machines.

A program of the book, e.g. code/p15_3_1.st, is tested by the Python program of the same name (code/p15_3_1.py):

    from plcbook import run, read
    r = run(read("p15_3_1.st"), plant="press", tests=[...])
    out(passed=r["passed"], total=r["total"])

The build fails when a test fails or the program does not compile, so every listing in the book is a program that works.
Node.js runs the engine (textbook/tools/plcrun.mjs → services/gateway/app/production/labkit/plc.js).
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> str:
    """A program file next to the calling program (the build runs programs in their code/ folder)."""
    return Path(name).read_text(encoding="utf-8")


def program(text: str, lang: str = "ST") -> dict:
    if lang == "LD":
        d = json.loads(text)
        return {"decls": d.get("decls", ""), "ladder": d["ladder"]}
    return {"st": text}


def run(text: str, *, lang: str = "ST", plant: str | None = None, io: list | None = None, tests: list | None = None,
        scenario: dict | None = None, review: bool = False, cycle: int = 10, plant_opts: dict | None = None, must_pass: bool = True) -> dict:
    node = shutil.which("node")
    if not node:
        raise SystemExit("plcbook: Node.js is needed to run the PLC programs")
    job = {"program": program(text, lang), "plant": plant, "io": io, "tests": tests or [], "scenario": scenario,
           "review": review, "cycle": cycle, "plantOpts": plant_opts or {}}
    r = subprocess.run([node, str(HERE / "plcrun.mjs")], input=json.dumps(job, ensure_ascii=False), capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise SystemExit("plcbook: " + (r.stderr.strip().splitlines() or ["node failed"])[-1])
    res = json.loads(r.stdout)
    if res.get("error"):
        raise SystemExit("plcbook: the program does not compile: " + res["error"])
    res["total"] = len(res["tests"])
    res["passed"] = sum(1 for t in res["tests"] if t["ok"])
    if must_pass and res["passed"] != res["total"]:
        bad = [f"{t['id']}: {t['failures'][:1]}" for t in res["tests"] if not t["ok"]]
        raise SystemExit("plcbook: tests failed: " + "; ".join(bad))
    if scenario is not None and must_pass and not res["scenario"]["ok"]:
        raise SystemExit("plcbook: the scenario failed: " + "; ".join(res["scenario"]["failures"][:2]))
    return res
