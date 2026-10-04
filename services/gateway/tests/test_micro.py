"""Microelectronics labs (第 17 轮附 3.3): the gateway forwards Verilog to the real micro-synth service (run in-process);
signed links for lab pages; rate limit; the service being off, busy or down."""
import importlib.util
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main, micro
from app.ai import ModelGateway
from app.moodle import MoodleClient
from tests.test_materials import BASE, fake_moodle, login

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("synth_app", ROOT / "services" / "micro-synth" / "app.py")
synth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(synth)

COUNTER = """module counter4(input clk, input rst, input en, output reg [3:0] q);
  always @(posedge clk) if (rst) q <= 4'd0; else if (en) q <= q + 4'd1;
endmodule"""
DOWN = {"on": False}


def other(request: httpx.Request) -> httpx.Response:
    if request.url.host == "down.test":
        raise httpx.ConnectError("refused")
    return fake_moodle(request)


@pytest.fixture
def client():
    with TestClient(main.app) as c:
        st = main.state.settings
        saved = {k: getattr(st, k) for k in ("microsynth_url", "public_url")}
        st.microsynth_url, st.public_url = "http://micro-synth.test", "https://learn.test"
        main.state.http = httpx.AsyncClient(mounts={"http://micro-synth.test": httpx.ASGITransport(app=synth.app),
                                                    "all://": httpx.MockTransport(other)})
        main.state.moodle = MoodleClient(BASE, "moodle_mobile_app", main.state.http)
        main.state.ai = ModelGateway("fake", main.state.http)
        yield c
        for k, v in saved.items():
            setattr(st, k, v)


def test_synth_signed_in(client, monkeypatch):
    monkeypatch.setattr(micro, "PER_MINUTE", 100)
    h = login(client, "s")
    r = client.post("/api/v1/micro/synth", headers=h, json={"source": COUNTER})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["ok"] and d["top"] == "counter4" and "counter4" in d["json"]["modules"]


def test_needs_sign_in(client):
    assert client.post("/api/v1/micro/synth", json={"source": COUNTER}).status_code == 401


def test_signed_link(client):
    h = login(client, "s")
    link = client.get("/api/v1/micro/synth-link", headers=h).json()
    assert link["on"] and link["synth_url"].startswith("https://learn.test/api/v1/micro-synth/")
    assert link["url"].startswith("https://learn.test/api/v1/micro-verilog/")
    path = link["synth_url"].replace("https://learn.test", "")
    d = client.post(path, json={"source": COUNTER}).json()
    assert d["ok"]
    assert client.post("/api/v1/micro-synth/not-a-token", json={"source": COUNTER}).status_code == 410
    # the page served by the gateway posts to the same site, to this user's signed address
    page = client.get(link["url"].replace("https://learn.test", ""))
    assert page.status_code == 200 and f'window.WQ_SYNTH_URL = "{path}"' in page.text and "DigitalJS" in page.text
    assert client.get("/api/v1/micro-verilog/not-a-token").status_code == 410


def test_link_tampered_or_expired(client, monkeypatch):
    h = login(client, "s")
    path = client.get("/api/v1/micro/synth-link", headers=h).json()["synth_url"].replace("https://learn.test", "")
    tampered = path[:-6] + ("AAAAAA" if not path.endswith("AAAAAA") else "BBBBBB")
    assert client.post(tampered, json={"source": COUNTER}).status_code == 410
    monkeypatch.setattr(micro, "LINK_TTL", -1)    # every link is past its lifetime
    assert client.post(path, json={"source": COUNTER}).status_code == 410


def test_errors_pass_through(client):
    h = login(client, "s")
    d = client.post("/api/v1/micro/synth", headers=h, json={"source": "module m(input a output b); endmodule"}).json()
    assert not d["ok"] and d["error"] == "yosys"
    assert client.post("/api/v1/micro/synth", headers=h, json={"source": "x" * (64 * 1024 + 1)}).status_code == 422


def test_rate_limit(client, monkeypatch):
    monkeypatch.setattr(micro, "PER_MINUTE", 3)
    h = login(client, "t")
    codes = [client.post("/api/v1/micro/synth", headers=h, json={"source": COUNTER}).status_code for _ in range(5)]
    assert codes[:3] == [200, 200, 200] and codes[3:] == [429, 429]


def test_off_and_down(client):
    h = login(client, "s")
    st = main.state.settings
    st.microsynth_url = ""
    r = client.post("/api/v1/micro/synth", headers=h, json={"source": COUNTER})
    assert r.status_code == 503 and r.json()["error"] == "unavailable"
    assert client.get("/api/v1/micro/synth-link", headers=h).json()["on"] is False
    st.microsynth_url = "http://down.test"
    r = client.post("/api/v1/micro/synth", headers=h, json={"source": COUNTER})
    assert r.status_code == 503
