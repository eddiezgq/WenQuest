"""第 54 轮：电脑横机——计算核心逐项对上教材第 17 章（17.3、17.7、17.8 节算例和习题），再走一遍网页接口、CAE、优化、AI 规则版。"""
import io
import json
import zipfile

import pytest

from app.sewcore import flatknit as K
from app.sewcore import optimize as OPT
from tests.test_course_pack import client  # noqa: F401
from tests.test_materials import login
from tests.test_sewing_api import sc  # noqa: F401
from tests.test_sewing_cae import cae, done  # noqa: F401


def chk(R, key):
    return next(c for c in R["checks"] if c["key"] == key)


def test_design_example_17_8():
    """17.8 节：E12、275 针、单系统、1.2 m/s、10 m/s²、760 横列 → 一趟 876 mm / 0.90 s，一片 11.4 min；三个改进方向"""
    p = K.clean({})
    assert K.pitch(12) == pytest.approx(2.117, abs=1e-3)
    assert K.margin(p) == pytest.approx(72, abs=0.01)
    pr = K.production(p)
    assert pr["D"] == pytest.approx(876, abs=0.5) and pr["t_pass"] == pytest.approx(0.90, abs=0.005)
    assert pr["passes"] == 760 and pr["t_piece"] / 60 == pytest.approx(11.4, abs=0.05)
    assert K.production(p, comp="realtime")["t_piece"] / 60 == pytest.approx(10.3, abs=0.05)          # 方案 A：c 减到 20 mm
    b = K.production(p, sys=2)
    assert b["passes"] == 460 and b["t_piece"] / 60 == pytest.approx(7.9, abs=0.05)                  # 方案 B：两系统
    c = K.production(p, v=1.6)
    assert c["t_piece"] / 60 == pytest.approx(10.5, abs=0.05) and K.margin(dict(p, v=1.6)) == pytest.approx(128, abs=0.01)
    assert (1 - c["t_piece"] / pr["t_piece"]) * 100 == pytest.approx(8, abs=0.5)                   # 提速 33% 只快 8%


def test_selection_17_3_and_exercises():
    R = K.analyze({})
    assert R["ok"] and all(c["state"] == "ok" for c in R["checks"])
    assert chk(R, "sel_time")["value"]["zh"].startswith("t_n = 1.76 ms")
    # 不补偿：全速滞后 v·T_d = 0.34 个针距 → 红
    assert K.sel_error(K.clean({"comp": "none"}), 300) == pytest.approx(0.34, abs=0.005)
    assert chk(K.analyze({"comp": "none"}), "sel_err")["state"] == "bad"
    # E18 同速选针器跟不上；v ≤ p/T_c = 1.17 m/s 就行（17.8 第 1 步）
    assert chk(K.analyze({"E": 18}), "sel_time")["state"] == "bad"
    assert chk(K.analyze({"E": 18, "v": 1.15}), "sel_time")["state"] == "ok"
    assert chk(K.analyze({"E": 18, "seg": 2}), "sel_time")["state"] == "ok"                         # 多段选针
    # 习题 1、2：E7 / E16 1.0 m/s 的 t_n；E14 不补偿滞后约 0.33 p
    assert K.pitch(7) / 1.0 == pytest.approx(3.63, abs=0.01) and K.pitch(16) / 1.0 == pytest.approx(1.59, abs=0.01)
    assert K.sel_error(K.clean({"E": 14, "Td": 0.5, "comp": "none"}), 300) == pytest.approx(0.33, abs=0.01)
    # 制动 1.2 m/s、20 m/s²：36 mm；提速到 1.6 m/s 就超出 50 mm 的余量
    assert chk(R, "brake")["value"]["zh"].startswith("36 / 122")              # 在最后一枚针处全速急停：换向余量 72 + 端部 50
    assert chk(K.analyze({"v": 1.6}), "brake")["state"] == "ok" and chk(K.analyze({"v": 2.0, "e_end": 10, "comp": "realtime"}), "brake")["state"] == "bad"


def test_closed_loop_and_racking_and_motor():
    # 17.7 节算例：N = 275、l* = 5.0、实测 1400 mm → Δl 0.091、Δd ≈ −0.023 mm、浅 2 步；习题 6：N 200、l* 6.0、1176 mm
    c = K.loop_correction(K.clean({}), 1400, 275)
    assert c["dl"] == pytest.approx(0.091, abs=1e-3) and c["dd"] == pytest.approx(-0.023, abs=1e-3) and round(c["steps"]) == -2
    assert K.loop_correction(K.clean({"lstar": 6.0}), 1176, 200)["dd"] == pytest.approx(0.03, abs=1e-3)
    R = K.analyze({})
    assert chk(R, "cam_res")["value"]["zh"] == "0.40%"                 # 每步 0.01 mm × ∂l/∂d 2 = 0.02 mm，l* 5 mm 的 0.4%
    assert chk(K.analyze({"step": 0.05}), "cam_res")["state"] == "bad"
    assert chk(K.analyze({"meas": 0.8}), "meas")["state"] == "warn"
    assert chk(K.analyze({"ar": 1}), "rack")["state"] == "bad"
    d = K.drive(K.clean({}))
    assert d["m"] == 40 and d["F"] == pytest.approx(440) and d["rpm"] == pytest.approx(1146, abs=1)
    assert chk(K.analyze({"sys": 3}), "m_rms")["state"] == "bad"       # 三系统机头 70 kg，原电机发热超额定
    # 改进方案表：提速那一行有一盏红灯（制动），加系统那一行没有
    rows = next(t for t in R["tables"] if t["key"] == "variants")["rows"]
    assert rows[2][3] == "7.9" and rows[2][5] == "0" and rows[3][3] == "10.5"
    # 并排织三只袖口，每片的时间比单织一只短得多（习题 7 的结论）
    one = K.production(K.clean({"N": 100}))["t_piece"]
    three = K.production(K.clean({"N": 100, "pcs": 3, "gap": 0}))["t_piece"]
    assert three < one * 0.6
    g = R["garment"]
    assert g["E_eff"] == 6 and g["total_pieces"] == pytest.approx(g["knit_pieces"] + 25)
    assert K.width(K.clean({"fashion": "whole"})) == pytest.approx(2 * K.width(K.clean({})))      # 隔针编织占两倍针床宽


def test_edge_cases_do_not_break():
    assert K.analyze({"rib": 0, "jac": 0, "xfer": 0})["production"]["passes"] == 1                 # 三项都是 0 也不除零
    R = K.analyze({"v": 2.0, "a": 2.0, "comp": "realtime"})                                   # 行程短，到不了最高速度：三角形速度
    vp, ta, tc, tm = K.profile(R["production"]["D"], 2.0, 2.0)
    assert tc == pytest.approx(0, abs=1e-9) and vp < 2.0 and R["production"]["t_pass"] == pytest.approx(tm + 0.05)
    assert all(0 <= t["a"] < t["b"] <= 360 for t in R["timing"]) and "run" not in [t["key"] for t in R["timing"]]
    assert K.analyze({"E": 18})["results"][1]["value"] == "1.17"                                  # 往小取
    assert len(K.analyze({"v": 2.0})["tables"][0]["rows"]) == 3                                   # 已经最快就不列“提速”


def test_optimizer_finds_systems_not_speed():
    r = OPT.run("flatknit", {}, "time")
    best = r["candidates"][0]
    assert best["bad"] == 0 and best["params"]["sys"] >= 2 and best["value"] < 11.4 * 0.7
    assert OPT.goals("flatknit")[0]["key"] == "time"


def test_api_exports_and_proto(sc, tmp_path):  # noqa: F811
    c = sc
    s = c.get("/api/v1/sewing/schema?machine=flatknit").json()
    keys = [p["key"] for g in s["groups"] for p in g["params"]]
    assert {"E", "v", "comp", "Td", "TmR", "fashion"} <= set(keys) and "step" not in s["kinds"]
    r = c.post("/api/v1/sewing/analyze", json={"machine": "flatknit", "params": {"E": 18}}).json()
    assert not r["ok"] and r["view"]["page"] == "model-flatknit" and r["timing_x"] == "pass"
    admin = login(c)
    for kind in ("report", "card", "params"):
        x = c.post(f"/api/v1/sewing/export/{kind}", json={"machine": "flatknit", "params": {}, "project": "FK-1"}, headers=admin)
        assert x.status_code == 200 and x.content.startswith(b"PK"), kind
    assert c.post("/api/v1/sewing/export/step", json={"machine": "flatknit", "params": {}}, headers=admin).status_code == 404
    assert c.post("/api/v1/sewing/export/json", json={"machine": "flatknit", "params": {}}, headers=admin).json()["machine"] == "flatknit"
    z = zipfile.ZipFile(io.BytesIO(c.get("/api/v1/sewing/freecad.zip", headers=admin).content))
    assert "Mod/WenQuestSewing/sewcore/flatknit.py" in z.namelist()
    d = tmp_path / "textbook" / "sewing" / "webed" / "labs"
    d.mkdir(parents=True)
    (d / "model-flatknit.html").write_text("<html>flatknit</html>", encoding="utf-8")
    assert "flatknit" in c.get("/api/v1/sewing/proto?page=model-flatknit").text


def test_cae_motor_frame_optimize(cae):  # noqa: F811
    c, h, fk = cae
    o = c.get("/api/v1/sewing/cae/options?machine=flatknit", headers=h).json()
    assert o["parts"] == [] and o["cam_parts"] == [] and o["kinds"]["motor"] and o["kinds"]["xy"] and not o["kinds"]["mbd"]
    assert [g["key"] for g in o["goals"]] == ["time"]
    m = c.post("/api/v1/sewing/cae/motor", json={"machine": "flatknit", "params": {}}, headers=h).json()
    ax = m["axes"][0]
    assert ax["key"] == "carriage" and ax["mass"] == 40 and ax["force"] == pytest.approx(440)
    assert ax["current"]["rated"] == 3.18 and all(r["need_peak"] > 0 for r in ax["rows"])
    # 针床 / 机架模态：判据 f1 × 机头加速时间 v/a ≥ 1.5
    fk.desc = None
    r = c.post("/api/v1/sewing/cae/frame", files={"file": ("bed.step", b"ISO-10303-21;", "application/step")},
               data={"machine": "flatknit", "params": json.dumps({}), "material": "HT200"}, headers=h).json()
    j = done(c, h, fk, r["id"])
    assert "针床" in j["title"] and j["result"]["checks"][0]["key"] == "xy_res" and "机头加速" in j["result"]["checks"][0]["zh"]
    assert j["result"]["t_move"] == pytest.approx(0.12)
    r = c.post("/api/v1/sewing/optimize", json={"machine": "flatknit", "params": {}, "goal": "time"}, headers=h).json()
    assert r["candidates"][0]["bad"] == 0


def test_ai_rules(client, monkeypatch):  # noqa: F811
    from app import main
    monkeypatch.setattr(main.state.ai, "provider", "none")
    r = client.post("/api/v1/sewing/ai/draft", json={"machine": "flatknit", "params": {}, "sentence": "机号改成 14，机头速度 1.3"},
                    headers=login(client)).json()
    assert r["model"] == "rules" and {x["key"]: x["new"] for x in r["changes"]} == {"E": 14, "v": 1.3}
