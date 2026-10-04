"""WenQuest Verilog synthesis service (第 17 轮附 3.3): Yosys on the server for phones.

POST /synth {source, top?} → {ok, json (Yosys write_json netlist), stat (text), top, seconds} or {ok: false, error, log}.
The phone page then simulates the netlist with DigitalJS in the browser, as the desktop page does with WebAssembly Yosys.

Limits: source ≤ 64 KB; one synthesis ≤ 20 s (killed after); at most 2 at a time, the rest wait up to 30 s.
The script is fixed (read_verilog → proc → opt → memory → wreduce → write_json → stat): the student only supplies
Verilog, never Yosys commands, and `read_verilog` gets no include paths, so a design cannot read other files.
No secrets, no internet (internal network only); the container runs read-only with a small /tmp.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import tempfile
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

MAX_SOURCE = 64 * 1024
TIMEOUT = float(os.environ.get("SYNTH_TIMEOUT", "20"))
PARALLEL = int(os.environ.get("SYNTH_PARALLEL", "2"))
QUEUE_WAIT = 30.0
YOSYS = os.environ.get("YOSYS", "yosys")
TOP = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]{0,63}$")
# Verilog features that reach outside the design: file reads and includes are refused before Yosys sees them.
FORBIDDEN = re.compile(r"`include|\$readmem[bh]|\$fopen|\$fread|\$fscanf|\$system", re.I)

app = FastAPI(title="WenQuest Verilog synthesis")
SLOTS = asyncio.Semaphore(PARALLEL)
DONE = {"ok": 0, "failed": 0, "timeout": 0, "busy": 0}


class SynthIn(BaseModel):
    source: str = Field(min_length=1, max_length=MAX_SOURCE)
    top: str | None = Field(default=None, max_length=64)


def script(top: str | None) -> str:
    hier = f"hierarchy -check -top {top}; " if top else "hierarchy -check -auto-top; "
    return ("read_verilog -nooverwrite top.v; " + hier +
            "proc; opt; memory; opt; wreduce; opt_clean; write_json out.json; tee -q -o stat.txt stat")


def clean_log(text: str) -> str:
    """Keep Yosys' messages useful to a student (errors, warnings), drop paths and banners."""
    lines = [ln for ln in text.splitlines() if ln.strip() and ("ERROR" in ln or "Warning" in ln or "error" in ln)]
    return "\n".join(lines[-40:])[:4000]


async def run_yosys(source: str, top: str | None) -> dict:
    with tempfile.TemporaryDirectory(prefix="synth-") as d:
        with open(os.path.join(d, "top.v"), "w", encoding="utf-8") as f:
            f.write(source)
        proc = await asyncio.create_subprocess_exec(
            YOSYS, "-q", "-p", script(top), cwd=d,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return {"ok": False, "error": "timeout", "log": f"synthesis took longer than {int(TIMEOUT)} s"}
        log = out.decode("utf-8", "replace")
        path = os.path.join(d, "out.json")
        if proc.returncode != 0 or not os.path.exists(path):
            return {"ok": False, "error": "yosys", "log": clean_log(log) or "Yosys could not synthesise this design"}
        with open(path, encoding="utf-8") as f:
            netlist = json.load(f)
        stat = ""
        sp = os.path.join(d, "stat.txt")
        if os.path.exists(sp):
            with open(sp, encoding="utf-8", errors="replace") as f:
                stat = f.read()[-6000:]
        tops = [m for m, v in netlist.get("modules", {}).items() if str(v.get("attributes", {}).get("top", "0")).strip("0") != ""]
        return {"ok": True, "json": netlist, "stat": stat, "top": tops[0] if tops else top, "warnings": clean_log(log)}


@app.get("/health")
async def health():
    return {"ok": True, "parallel": PARALLEL, **DONE}


@app.post("/synth")
async def synth(body: SynthIn):
    if body.top is not None and not TOP.match(body.top):
        return JSONResponse({"ok": False, "error": "bad_top", "log": "the top module name is not a Verilog identifier"}, status_code=422)
    if FORBIDDEN.search(body.source):
        return JSONResponse({"ok": False, "error": "forbidden", "log": "`include, $readmem and file functions are not allowed here"}, status_code=422)
    t0 = time.monotonic()
    try:
        await asyncio.wait_for(SLOTS.acquire(), QUEUE_WAIT)
    except asyncio.TimeoutError:
        DONE["busy"] += 1
        return JSONResponse({"ok": False, "error": "busy", "log": "the synthesis service is busy, try again in a minute"}, status_code=503)
    try:
        out = await run_yosys(body.source, body.top)
    finally:
        SLOTS.release()
    DONE["ok" if out["ok"] else ("timeout" if out.get("error") == "timeout" else "failed")] += 1
    out["seconds"] = round(time.monotonic() - t0, 3)
    return out
