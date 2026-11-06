"""第 105 轮：起草台服务。模型用替身（不经网关、不调真模型）；仿真关掉（EDA_SIM=0），仿真核对在 eda/tests 里测。"""

import os
import sys

os.environ.setdefault("EDA_SIM", "0")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402
import yaml  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app as A  # noqa: E402

REQ = "给 400 W、48 V 的机器人关节伺服电机做一块驱动板，额定相电流 8.5 A，峰值 30 A，带 2500 线增量编码器和 CAN。"


def S(key, value, source="requirement", quote="", why=""):
    return {"key": key, "value": value, "source": source, "quote": quote, "why": why}


GOOD = {"spec": [S("bus_voltage_v", 48, quote="48 V"), S("phase_current_a", 8.5, quote="额定相电流 8.5 A"),
                 S("phase_current_peak_a", 30, quote="峰值 30 A")],
        "units": [{"type": "encoder", "params": [S("lines", 2500, quote="2500 线")]}],
        "questions": ["最高转速是多少？"], "unsupported": ["EtherCAT 目录里没有"]}


@pytest.fixture
def client(monkeypatch):
    verdicts = []

    def fake_gateway(request):
        if not A._headers(request):
            from fastapi import HTTPException
            raise HTTPException(401, {"en": "sign in", "zh": "请先登录"})

        def model(requirement, catalog, lang, feedback):
            assert "default" not in catalog["spec"][0]
            return GOOD, 7

        return model, lambda rid, passed, note: verdicts.append((rid, passed, note))

    monkeypatch.setattr(A, "gateway_model", fake_gateway)
    c = TestClient(A.app)
    c.verdicts = verdicts
    return c


def test_health_and_catalog(client):
    assert client.get("/api/health").json()["ok"]
    cat = client.get("/api/catalog").json()
    assert {u["type"] for u in cat["units"]} >= {"bus_input", "gate_drive", "encoder"}


def test_draft_needs_login(client):
    assert client.post("/api/draft", json={"requirement": REQ}).status_code == 401


def test_draft_then_edit_then_download(client):
    h = {"cookie": "wq_sso=x"}
    r = client.post("/api/draft", json={"requirement": REQ}, headers=h).json()
    assert r["report"]["missing"] == [] and r["result"]["count"]["fail"] == 0
    assert r["report"]["unsupported"] == ["EtherCAT 目录里没有"]
    assert client.verdicts == [(7, True, "退回 0 处；缺 无；不通过 0")]
    doc = yaml.safe_load(r["result"]["yaml"])
    assert doc["spec"]["bus_voltage_v"] == 48 and doc["draft"]["runs"] == [7]
    vals = {"spec": {"bus_voltage_v": 24, "phase_current_a": 8.5, "phase_current_peak_a": 30},
            "params": {"encoder": {"lines": 2500}, "gate_drive": {"RG_OHM": 10.0}}}
    body = {"requirement": REQ, "report": r["report"], "values": vals, "runs": [7]}
    e = client.post("/api/evaluate", json=body).json()
    assert e["report"]["spec"]["bus_voltage_v"]["source"] == "person"
    assert e["report"]["questions"] == ["最高转速是多少？"]
    doc = yaml.safe_load(e["result"]["yaml"])
    assert doc["spec"]["bus_voltage_v"] == 24
    assert doc["draft"]["provenance"]["spec"]["bus_voltage_v"]["source"] == "person"
    assert "| 母线电压 | 24 V |" in e["result"]["markdown"] and e["result"]["count"]["fail"] == 0


def test_evaluate_rejects_out_of_range_and_reports_missing(client):
    r = client.post("/api/evaluate", json={"values": {"spec": {"bus_voltage_v": 400}}})
    assert r.status_code == 400 and "超出" in r.json()["detail"]["zh"]
    r = client.post("/api/evaluate", json={"values": {"spec": {"bus_voltage_v": 48}}}).json()
    assert r["result"] is None and set(r["report"]["missing"]) == {"phase_current_a", "phase_current_peak_a"}


def test_requirement_length(client):
    assert client.post("/api/draft", json={"requirement": "a"}, headers={"cookie": "x=1"}).status_code == 400
