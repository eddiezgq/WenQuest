"""第 81 轮：花样机、刺绣机、横机的样机跟设计同步——计算核心给样机的轨迹（每针 / 每趟）和计算一致，出问题的针 / 趟和校核一致，轨迹有上限。"""
import base64

import pytest

from app.sewcore import embroid as E
from app.sewcore import emb_samples as SMP
from app.sewcore import flatknit as F
from app.sewcore import knit_samples as KS
from app.sewcore import pattern as P
from app.sewcore.common import TRACK_MAX, thin

LOGO = base64.b64encode(SMP.logo_dst()).decode()


def test_pattern_track_follows_the_plan():
    R = P.analyze({"pat": "star", "n": 3000, "ax": 5})
    v = R["view"]
    c = v["cfg"]
    PL = P.plan(R["params"])
    assert v["page"] == "model-pattern" and v["sync"] == "setCfg" and c["N"] == len(PL["pts"]) == c["n"]
    assert c["sp"] == [round(x) for x in PL["speeds"]]
    usable = 360 - (c["f2"] - c["f1"]) - 2 * c["mg"]
    assert max(c["mv"]) <= usable + 0.2                                   # 前瞻以后每一针都在窗口里走完
    w = c["worst"]
    assert c["cap"][w] == min(c["cap"][1:])                               # 最紧的那一针
    bad = [x["key"] for x in c["bad"] if x["state"] == "bad"]
    assert bad == [k["key"] for k in R["checks"] if k["state"] == "bad"] and "speed" in bad
    assert not P.analyze({})["view"]["cfg"]["bad"]
    far = P.analyze({"stx": 40})["view"]["cfg"]
    assert "travel" in [x["key"] for x in far["bad"]] and abs(far["pts"][far["far"]][0]) >= 30


def test_pattern_csv_track_and_thinning():
    pts = "\n".join(f"{i * 0.5 % 80:.1f},{(i // 160) * 2:.1f}" for i in range(9000))
    c = P.analyze({"pat": "csv", "pts": pts})["view"]["cfg"]
    assert c["N"] == P.MAX_PTS and c["n"] <= TRACK_MAX and len(c["pts"]) == len(c["sp"]) == len(c["mv"]) == c["n"]
    idx = thin(20000, keep=(12345,))
    assert len(idx) <= TRACK_MAX and idx[0] == 0 and idx[-1] == 19999 and 12345 in idx and idx == sorted(set(idx))
    assert thin(10) == list(range(10))


def test_embroid_track_file_and_manual():
    R = E.analyze({"src": "file", "dst": LOGO, "H": 12})
    c = R["view"]["cfg"]
    PL = E.plan(E.clean({"src": "file", "dst": LOGO, "H": 12}))
    assert R["view"]["page"] == "model-embroid" and c["N"] == len(PL["sp"]) and c["n"] <= TRACK_MAX and c["file"]
    i = c["idx"][c["worst"]]
    assert c["L"][c["worst"]] == pytest.approx(PL["s"][i], abs=0.01) and c["sp"][c["worst"]] == round(PL["sp"][i])
    assert max(c["acc"]) <= 1.0 + 1e-3 and max(c["col"]) == 5             # 前瞻以后都走得完；5 次换色
    # 手填：按设计转速画一段最长针的缎纹；走不完时所需 / 可用 > 1，和校核一致
    m = E.analyze({"H": 12, "F": 300})["view"]["cfg"]
    assert not m["file"] and m["L"][1] == 7.0 and m["sp"][1] == 650 and m["acc"][m["worst"]] > 1
    assert [x["key"] for x in m["bad"]] == ["accel"] and m["H"] == 12
    ok = E.analyze({})["view"]["cfg"]
    assert ok["acc"][ok["worst"]] <= 1 and not ok["bad"]


def test_flatknit_track_passes():
    R = F.analyze({})
    c = R["view"]["cfg"]
    PR = R["production"]
    assert R["view"]["sync"] == "setCfg" and c["N"] == PR["passes"] == 760 and c["kind"].count("x") == R["params"]["xfer"]
    assert sum(c["t"]) == pytest.approx(PR["t_piece"] * R["params"]["pcs"], rel=1e-3) and c["tacc"][-1] == pytest.approx(sum(c["t"]), abs=0.05)
    r = F.analyze({"rack": 4, "tset": 200})["view"]["cfg"]
    assert "rack" in [x["key"] for x in r["bad"]] and r["kind"][r["first_x"]] == "x"
    d = F.analyze({"src": "file", "knit": KS.front_text(), "sys": 2})
    c = d["view"]["cfg"]
    assert c["N"] == d["production"]["passes"] and c["sys"] == 2 and set(c["kind"]) <= {"k", "x", "e"}
    assert c["D"][c["widest"]] == max(c["D"]) and c["W"] == pytest.approx(F.width(d["params"] | {"knit": KS.front_text()}), abs=0.1)


def test_review_fixes():
    """独立审读后改的：全成型按倍数折算用时；手填刺绣按设计转速；抽样跳过跳步 / 换色时抬笔；收针翻针均匀插"""
    r = F.analyze({"fashion": "whole"})
    c = r["view"]["cfg"]
    assert c["kw"] == r["params"]["kwhole"] and sum(c["t"]) == pytest.approx(r["production"]["t_piece"] * r["params"]["pcs"], rel=1e-3)
    xs = [i for i, k in enumerate(F.analyze({})["view"]["cfg"]["kind"]) if k == "x"]
    gaps = [b - a for a, b in zip(xs, xs[1:])]
    assert max(gaps) - min(gaps) <= 2                                      # 不挤在最后
    m = E.analyze({"H": 4, "F": 1050, "n": 1300, "n_head": 1000})["view"]["cfg"]
    assert m["sp"][1] == 1300 and (m["acc"][m["worst"]] > 1) == ("accel" in [x["key"] for x in m["bad"]])
    c = E.analyze({"src": "file", "dst": LOGO})["view"]["cfg"]
    assert len(c["up"]) == c["n"] and sum(c["up"]) > 0 and c["over"] is None
