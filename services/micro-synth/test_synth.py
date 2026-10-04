"""micro-synth: a counter and the PWM generator synthesise; syntax errors, forbidden constructs, bad top names,
oversized sources and runaway designs are refused; at most PARALLEL syntheses run at once."""
import asyncio
import os

import pytest
from fastapi.testclient import TestClient

import app as synth

COUNTER = """module counter4(input clk, input rst, input en, output reg [3:0] q);
  always @(posedge clk) if (rst) q <= 4'd0; else if (en) q <= q + 4'd1;
endmodule"""
PWM = """module pwm4(input clk, input rst, input [3:0] duty, output out);
  reg [3:0] cnt;
  always @(posedge clk) if (rst) cnt <= 4'd0; else cnt <= cnt + 4'd1;
  assign out = (cnt < duty);
endmodule"""

c = TestClient(synth.app)


def test_counter():
    r = c.post("/synth", json={"source": COUNTER}).json()
    assert r["ok"] and r["top"] == "counter4"
    assert "counter4" in r["json"]["modules"]
    ports = r["json"]["modules"]["counter4"]["ports"]
    assert set(ports) == {"clk", "rst", "en", "q"} and len(ports["q"]["bits"]) == 4
    assert "cells" in r["stat"].lower()


def test_pwm_with_top():
    r = c.post("/synth", json={"source": PWM + "\nmodule other(input a, output b); assign b = ~a; endmodule", "top": "pwm4"}).json()
    assert r["ok"] and r["top"] == "pwm4"


def test_syntax_error():
    r = c.post("/synth", json={"source": "module m(input a, output b) assign b = a; endmodule"}).json()
    assert not r["ok"] and r["error"] == "yosys" and r["log"]


@pytest.mark.parametrize("bad", ['`include "/etc/passwd"\nmodule m; endmodule',
                                 'module m; initial $readmemh("/etc/passwd", x); endmodule'])
def test_forbidden(bad):
    r = c.post("/synth", json={"source": bad})
    assert r.status_code == 422 and r.json()["error"] == "forbidden"


def test_bad_top():
    assert c.post("/synth", json={"source": COUNTER, "top": "x; shell rm"}).status_code == 422


def test_too_long():
    assert c.post("/synth", json={"source": "x" * (64 * 1024 + 1)}).status_code == 422


def test_timeout(monkeypatch, tmp_path):
    slow = tmp_path / "slow-yosys"                  # stands in for a design that keeps Yosys busy
    slow.write_text("#!/bin/sh\nsleep 5\n"); slow.chmod(0o755)
    monkeypatch.setattr(synth, "YOSYS", str(slow))
    monkeypatch.setattr(synth, "TIMEOUT", 0.3)
    r = c.post("/synth", json={"source": COUNTER}).json()
    assert not r["ok"] and r["error"] == "timeout"


def test_parallel_limit(monkeypatch):
    running = {"now": 0, "max": 0}
    real = synth.run_yosys

    async def slow(src, top):
        running["now"] += 1
        running["max"] = max(running["max"], running["now"])
        await asyncio.sleep(0.2)
        running["now"] -= 1
        return {"ok": True, "json": {}, "stat": "", "top": None, "warnings": ""}

    monkeypatch.setattr(synth, "run_yosys", slow)
    monkeypatch.setattr(synth, "SLOTS", asyncio.Semaphore(2))

    async def go():
        import httpx
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=synth.app), base_url="http://t") as cl:
            await asyncio.gather(*[cl.post("/synth", json={"source": COUNTER}) for _ in range(6)])
    asyncio.run(go())
    assert running["max"] == 2
    monkeypatch.setattr(synth, "run_yosys", real)


@pytest.mark.parametrize("src", [
    "`define R $readmem``h\nmodule m(output [7:0] y); reg [7:0] x[0:0]; initial `R(\"/etc/hostname\", x); assign y = x[0]; endmodule",
    "`define F readmemh\nmodule m; endmodule",
    "module m; initial $ fopen(\"x\"); endmodule",
    "` include \"/etc/passwd\"\nmodule m; endmodule",
])
def test_forbidden_tricks(src):
    r = c.post("/synth", json={"source": src})
    assert r.status_code == 422 and r.json()["error"] == "forbidden"


def test_macros_still_allowed():
    src = "`timescale 1ns/1ps\n`define W 4\nmodule m(input [`W-1:0] a, output [`W-1:0] b); assign b = ~a; endmodule"
    assert c.post("/synth", json={"source": src}).json()["ok"]
