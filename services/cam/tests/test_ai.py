"""AI drafting (round 39, step 6): the code checks on what the model writes, and the cam service's endpoints with the
gateway replaced by a stand-in (no network, no real model).

Checks written out:
  - a number the model wrote that the sentence does not state is cleared (and reported), never used
  - one dwell left without an angle gets the rest of the turn; a closed program's one missing lift brings the
    follower back; two gaps are asked for, not guessed
  - a draft that passes is a valid program, and the cam's checks run on it before the user sees it
  - in explanations, a sentence with a number that is not in the check results is dropped
"""

import json
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

import cae_bridge as B
from app import app
from camkit import ai_check as AC
from camkit.program import Program

EX = Path(__file__).resolve().parents[1] / "examples"
S1 = "主轴转一圈：前 100° 用摆线规律推出 40 mm，停 80°，再用 120° 退回，其余停着"


def seg(kind, deg, h=None, law=None):
    return {"kind": kind, "deg": deg, "h": h, "law": law, "why": ""}


def test_good_draft_becomes_a_program():
    d = {"segments": [seg("rise", 100, 40, "cycloidal"), seg("dwell", 80), seg("return", 120, 40, "poly345"),
                      seg("dwell", None)], "advance_deg": None}
    r = AC.program_from_draft(d, "translating", S1)
    assert r["usable"] and not r["cleared"] and not r["missing"]
    assert r["filled"] == [{"seg": 4, "field": "deg", "value": 60.0, "why": "rest of the turn"}]
    Program.from_dict(r["program"])
    assert [s["deg"] for s in r["program"]["segments"]] == [100, 80, 120, 60.0]


def test_invented_numbers_are_cleared_and_asked_for():
    # the sentence gives no dwell angle and no return angle: the model "helpfully" wrote 90 and 50
    s = "前 100° 推出 40 mm，停一会儿，再退回"
    d = {"segments": [seg("rise", 100, 40, "cycloidal"), seg("dwell", 90), seg("return", 50, 40, "poly345"),
                      seg("dwell", None)], "advance_deg": None}
    r = AC.program_from_draft(d, "translating", s)
    assert {(c["seg"], c["field"]) for c in r["cleared"]} == {(2, "deg"), (3, "deg")}
    assert not r["usable"] and r["program"] is None
    assert {(m["seg"], m["field"]) for m in r["missing"]} >= {(2, "deg"), (3, "deg")}
    # an unknown law name is cleared too, and a lift the sentence does not give is never used
    d = {"segments": [seg("rise", 100, 45, "magic"), seg("dwell", 260)], "advance_deg": None}
    r = AC.program_from_draft(d, "translating", "前 100° 推出 40 mm，其余停")
    assert {(c["field"], c["value"]) for c in r["cleared"]} == {("h", 45), ("law", "magic"), ("deg", 260)}
    assert r["segments"][1]["deg"] == 260 and r["filled"][0]["why"] == "rest of the turn"  # refilled by code


def test_closed_program_return_lift_and_indexing_advance():
    d = {"segments": [seg("rise", 120, 30, "mod_sine"), seg("dwell", 60), seg("return", 120, None, "mod_sine"),
                      seg("dwell", 60)], "advance_deg": None}
    r = AC.program_from_draft(d, "oscillating", "120° 内摆 30°，停 60°，120° 摆回，停 60°")
    assert r["usable"] and r["program"]["segments"][2]["h_deg"] == 30 and r["program"]["unit"] == "rad"
    # an indexing turret: one rise of 45° per turn, the advance follows from it
    d = {"segments": [seg("dwell", 240), seg("rise", 120, 45, "mod_sine")], "advance_deg": None}
    r = AC.program_from_draft(d, "indexing", "八工位转塔：凸轮转 120° 分度 45°，其余 240° 停")
    assert r["usable"] and r["program"]["advance_deg"] == 45 and r["filled"][-1]["field"] == "advance"


def test_texts_keep_only_numbers_from_the_results():
    vals = AC.result_numbers([{"value": 39.0488, "limit": 40}, {"value": 1451.2, "limit": None}])
    kept, dropped = AC.keep_supported(["最大压力角 39.05°，低于许用值 40°。", "接触应力 1451 MPa。",
                                       "建议把基圆加到 70 mm。", "两个滚子同时在槽里。"], vals)
    assert kept == ["最大压力角 39.05°，低于许用值 40°。", "接触应力 1451 MPa。", "两个滚子同时在槽里。"]
    assert dropped == ["建议把基圆加到 70 mm。"]


# ------------------------------------------------------------------------------------------------ endpoints


def gateway_standin(drafts, sentences=("最大压力角 39.05°。", "改成 50 mm 基圆。")):
    seen = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append((req.url.path, json.loads(req.content or b"{}"), req.headers.get("cookie")))
        if not req.headers.get("cookie"):
            return httpx.Response(401, json={"error": "not_logged_in"})
        if req.url.path.endswith("/draft"):
            return httpx.Response(200, json={"draft": drafts.pop(0), "run": 7, "left_today": 29, "model": "fake"})
        if "/runs/" in req.url.path:
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(200, json={"sentences": list(sentences), "run": 8, "left_today": 28, "model": "fake"})
    return httpx.Client(transport=httpx.MockTransport(handler)), seen


def test_draft_endpoint(monkeypatch):
    p = json.loads((EX / "packaging-plate.json").read_text(encoding="utf-8"))
    good = {"segments": [seg("rise", 100, 40, "cycloidal"), seg("dwell", 80), seg("return", 120, 40, "poly345"),
                         seg("dwell", None)], "advance_deg": None, "assumptions": ["从 0° 开始"], "questions": []}
    cl, seen = gateway_standin([good, dict(good, segments=good["segments"][:1])])
    monkeypatch.setattr(B, "CLIENT", cl)
    c = TestClient(app)
    r = c.post("/api/ai/draft", json={"project": p, "sentence": S1})
    assert r.status_code == 401 and "登录" in r.json()["detail"]["zh"]
    c.cookies.set("wq_sso", "t")
    r = c.post("/api/ai/draft", json={"project": p, "sentence": S1}).json()
    assert r["check"]["usable"] and r["follower"] == "translating" and r["left_today"] == 29
    assert any(x["id"] == "phi_rise" for x in r["checks"])            # the cam's checks ran on the draft
    sent = next(b for path, b, _ in seen if path.endswith("/draft"))
    assert sent["sentence"] == S1 and "poly345" in sent["laws"]
    verdict = next(b for path, b, _ in seen if "/runs/7" in path)
    assert verdict["passed"] is True
    # a draft that leaves the turn short: not usable, no checks, the record says so
    r = c.post("/api/ai/draft", json={"project": p, "sentence": S1}).json()
    assert not r["check"]["usable"] and r["checks"] is None
    assert [b for path, b, _ in seen if "/runs/7" in path][-1]["passed"] is False


def test_explain_drops_invented_numbers(monkeypatch):
    p = json.loads((EX / "atc-globoidal.json").read_text(encoding="utf-8"))
    cl, seen = gateway_standin([], sentences=("换刀臂转动的最大压力角 39.05°。", "把中心距改到 185 mm 会更好。"))
    monkeypatch.setattr(B, "CLIENT", cl)
    c = TestClient(app)
    c.cookies.set("wq_sso", "t")
    r = c.post("/api/ai/explain", json={"project": p, "lang": "zh"}).json()
    assert r["sentences"] == ["换刀臂转动的最大压力角 39.05°。"] and r["dropped"] == 1
    sent = next(b for path, b, _ in seen if path.endswith("/explain"))
    assert any(x["id"] == "pressure" and x["group"] == "index" for x in sent["checks"])
