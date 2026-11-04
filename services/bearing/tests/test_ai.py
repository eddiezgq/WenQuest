"""AI drafts (round 64, step 7c): plain code decides what of a draft is kept. A number not in the sentence is cleared,
a field that is not the kind's is dropped, a word choice must be one of the options, the empty fields are listed; a
sentence of an explanation with a number not in the results is dropped. The gateway and the model are stand-ins."""

import copy
import json

import httpx
import pytest
from fastapi.testclient import TestClient

import app as A
import projects_api as P
from bearingkit import ai_check as AC
from bearingkit import fields as FL
from bearingkit.analyze import analyse

EX = A.EXAMPLES
GEAR = json.loads((EX / "scene-gearbox.json").read_text(encoding="utf-8"))
SENT = (
    "减速器输出轴，斜齿轮法向模数 3、齿数 34、法向压力角 20°、螺旋角 14°，功率 18 kW、转速 960 r/min，"
    "齿轮离 A 轴承 55 mm，跨距 160 mm，本轴承是 A，A 是固定端"
)


def test_kind_fields_follow_the_form():
    k = AC.kind_fields()
    assert set(k) == set(FL.SCENES)
    gear = {f["path"] for f in k["gearbox"]["fields"]}
    assert {"scenario.mn", "scenario.z", "scenario.x", "scenario.L", "scenario.cases", "scenario.fp"} <= gear
    assert "scenario.W" not in gear and "loads.Fr" not in gear
    assert {"loads.Fr", "loads.Fa", "loads.n"} <= {f["path"] for f in k["generic"]["fields"]}
    assert next(f for f in k["joint"]["fields"] if f["path"] == "scenario.axis")["options"] == [
        "horizontal",
        "vertical",
    ]
    assert next(f for f in k["spindle"]["fields"] if f["path"] == "scenario.cases")["columns"][1:3] == ["Fr", "Fa"]


def test_numbers_must_be_in_the_sentence():
    draft = {
        "kind": "gearbox",
        "values": [
            {"path": "scenario.mn", "value": 3, "quote": "法向模数 3"},
            {"path": "scenario.z", "value": 34, "quote": "齿数 34"},
            {"path": "scenario.alpha_n_deg", "value": 20, "quote": ""},
            {"path": "scenario.beta_deg", "value": 14, "quote": ""},
            {"path": "scenario.x", "value": 55, "quote": ""},
            {"path": "scenario.L", "value": 160, "quote": ""},
            {"path": "scenario.this", "value": "A", "quote": ""},
            {"path": "scenario.fixed", "value": "A", "quote": ""},
            {"path": "scenario.axial_to", "value": "C", "quote": ""},  # not an option: cleared
            {"path": "scenario.fp", "value": 1.2, "quote": ""},  # not in the sentence: cleared
            {"path": "scenario.W", "value": 500, "quote": ""},  # not a gearbox field: dropped
            {"path": "cases.0.P", "value": 18, "quote": ""},
            {"path": "cases.0.n", "value": 960, "quote": ""},
            {"path": "cases.0.share", "value": 1, "quote": ""},  # "1" is not in the sentence: cleared
            {"path": "cases.0.label", "value": "额定", "quote": ""},  # a word not in the sentence: cleared
            {"path": "cases.1.P", "value": 26, "quote": ""},  # invented second case: cleared
        ],
        "assumptions": [],
        "questions": [],
    }
    r = AC.apply_draft(draft, SENT, GEAR)
    s = r["project"]["scenario"]
    assert r["kind"] == "gearbox" and s["mn"] == 3 and s["z"] == 34 and isinstance(s["z"], int) and s["L"] == 160
    assert s["beta_deg"] == 14 and s["this"] == "A" and s["fixed"] == "A"
    assert s["axial_to"] == FL.FRESH["gearbox"]["axial_to"]  # the blank structure's choice, not the AI's "C"
    assert s["fp"] is None and "W" not in s
    assert s["cases"][0]["P"] == 18 and s["cases"][0]["n"] == 960 and s["cases"][0]["share"] is None
    assert len(s["cases"]) == 1  # the invented second case left nothing behind
    cleared = {c["path"] for c in r["cleared"]}
    assert cleared == {"scenario.axial_to", "scenario.fp", "cases.0.share", "cases.0.label", "cases.1.P"}
    assert [d["path"] for d in r["dropped"]] == ["scenario.W"]
    missing = {m["path"] for m in r["missing"]}
    assert "scenario.cases.0.share" in missing and not any(m.startswith("scenario.cases.1") for m in missing)
    assert "scenario.fp" not in missing  # may stay empty (no fatigue check)
    # nothing else of the project changed
    assert r["project"]["size"] == FL.normalise(GEAR)["size"] and r["project"]["type"] == GEAR["type"]


def test_units_are_not_converted_and_percent_may_be_a_fraction():
    sent = "通用：径向力 2.5 kN，轴向力 800 N，转速 3000 r/min"
    d = {
        "kind": "generic",
        "values": [
            {"path": "loads.Fr", "value": 2500, "quote": "2.5 kN"},
            {"path": "loads.Fa", "value": 800, "quote": ""},
            {"path": "loads.n", "value": 3000, "quote": ""},
        ],
        "assumptions": [],
        "questions": [],
    }
    r = AC.apply_draft(d, sent, GEAR)
    assert r["project"]["loads"]["Fr"] is None and [c["path"] for c in r["cleared"]] == ["loads.Fr"]
    assert {m["path"] for m in r["missing"]} == {"loads.Fr"}
    assert AC.sentence_numbers("直行 60%，转弯 20 ％") >= {0.6, 0.2, 60.0, 20.0}


def test_unknown_kind_and_a_full_draft_computes():
    assert AC.apply_draft({"kind": "rocket", "values": []}, SENT, GEAR)["error"]
    full = copy.deepcopy(GEAR["scenario"])
    vals = [
        {"path": "scenario." + k, "value": v, "quote": ""}
        for k, v in full.items()
        if k not in ("kind", "cases") and v is not None
    ]
    for i, c in enumerate(full.get("cases") or []):
        vals += [
            {"path": f"cases.{i}.{k}", "value": v, "quote": ""} for k, v in c.items() if v is not None and k != "label"
        ]
    sent = " ".join(str(v["value"]) if not isinstance(v["value"], dict) else v["value"].get("zh", "") for v in vals)
    r = AC.apply_draft({"kind": "gearbox", "values": vals}, sent, GEAR)
    assert not r["missing"] and not r["cleared"], (r["missing"], r["cleared"])
    a = analyse(r["project"])
    b = analyse(GEAR)
    assert [c["value"] for c in a["checks"]] == [c["value"] for c in b["checks"]]


def test_texts_keep_only_supported_numbers():
    vals = [1850.4, 0.0123, 7.36]
    kept, dropped = AC.keep_supported(
        [
            "外圈最大接触应力 1850 MPa，低于许用值。",
            "工作游隙 0.012 mm。",
            "建议把游隙加大到 0.020 mm。",
            "两个轴承都受载。",
        ],
        vals,
    )
    assert kept == ["外圈最大接触应力 1850 MPa，低于许用值。", "工作游隙 0.012 mm。", "两个轴承都受载。"]
    assert dropped == ["建议把游隙加大到 0.020 mm。"]


class Gateway:
    def __init__(self, draft, sentences):
        self.draft, self.sentences, self.calls = draft, sentences, []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.calls.append((request.method, request.url.path, request.content))
        if "nolicense" in (request.headers.get("cookie") or ""):
            return httpx.Response(403, json={})
        if request.url.path.endswith("/draft"):
            return httpx.Response(200, json={"draft": self.draft, "run": 7, "left_today": 29, "model": "fake"})
        if "/runs/" in request.url.path:
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(200, json={"sentences": self.sentences, "run": 8, "left_today": 28, "model": "fake"})


@pytest.fixture
def gw(monkeypatch):
    def make(draft, sentences=()):
        g = Gateway(draft, list(sentences))
        monkeypatch.setattr(P, "_CLIENT", [httpx.Client(transport=httpx.MockTransport(g))])
        return g

    return make


def test_api_draft_explain_and_errors(gw):
    g = gw(
        {
            "kind": "generic",
            "values": [
                {"path": "loads.Fr", "value": 4000, "quote": ""},
                {"path": "loads.n", "value": 3000, "quote": ""},
                {"path": "loads.Fa", "value": 900, "quote": ""},
            ],
        },
        ["外圈最大接触应力 9999 MPa。", "游隙已知。"],
    )
    c = TestClient(A.app)
    demo = json.loads((EX / "demo-deep-groove.json").read_text(encoding="utf-8"))
    body = {"project": {"project": demo, "sentence": "通用：径向力 4000 N，转速 3000 r/min", "lang": "zh"}}
    assert c.post("/api/ai/draft", json=body).status_code == 401  # not signed in
    c.cookies.set("wq_sso", "tok")
    r = c.post("/api/ai/draft", json=body).json()
    assert r["kind"] == "generic" and r["loads"]["Fr"] == 4000 and r["loads"]["Fa"] is None
    assert [x["path"] for x in r["cleared"]] == ["loads.Fa"] and r["status"] and r["checks"]
    sent = json.loads(g.calls[0][2])
    assert "generic" in sent["kinds"] and sent["bearing"] == "deep_groove"
    verdict = json.loads(g.calls[1][2])
    assert g.calls[1][1].endswith("/runs/7") and verdict["passed"] is False and "loads.Fa" in verdict["note"]
    t = c.post("/api/ai/explain", json={"project": {"project": demo, "lang": "zh"}}).json()
    assert t["sentences"] == ["游隙已知。"] and t["dropped"] == 1
    c.cookies.set("wq_sso", "nolicense")
    r = c.post("/api/ai/describe", json={"project": {"project": demo}})
    assert r.status_code == 403 and r.json()["detail"]["zh"] == "AI 起草给已开通的企业账号用，请联系问渠开通"
