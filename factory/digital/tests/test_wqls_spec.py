# -*- coding: utf-8 -*-
"""第 172 轮：WQ-LS 设计说明书网页版（/wqls/spec/）和原文 docs/设计/WQ-LS/ 一致，页面里的链接都打得开。
改了 docs/设计/WQ-LS/ 里任何文件、或改了 tools/wqls/spec_web.py，这条测试就失败：重跑 python3 tools/wqls/spec_web.py 再提交。"""
import importlib.util
import os
import re
import urllib.parse

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCRIPT = os.path.join(ROOT, "tools", "wqls", "spec_web.py")
SPEC = os.path.join(ROOT, "factory", "digital", "web", "public", "wqls", "spec")

# freecad-ai-parts 只同步了 factory/，没有 docs/ 和 tools/wqls/
pytestmark = pytest.mark.skipif(not os.path.exists(SCRIPT) or not os.path.isdir(os.path.join(ROOT, "docs", "设计", "WQ-LS")),
                                reason="没有 WQ-LS 原文（同步仓库）")


def _mod():
    spec = importlib.util.spec_from_file_location("spec_web", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_spec_matches_docs():
    assert _mod().check() == []


def test_every_doc_has_a_page_and_links_resolve():
    m = _mod()
    pages = set(os.listdir(SPEC))
    for rel in (p for p in os.listdir(os.path.join(ROOT, "docs", "设计", "WQ-LS")) if p.endswith(".md")):
        assert m.slug_page(rel) in pages
    for g in ("G1", "G2", "G3", "G4", "G5", "G6", "G8", "GC", "标准"):
        d = os.path.join(ROOT, "docs", "设计", "WQ-LS", g)
        for dp, _, fs in os.walk(d):
            for f in fs:
                if f.endswith(".md"):
                    rel = os.path.relpath(os.path.join(dp, f), os.path.join(ROOT, "docs", "设计", "WQ-LS"))
                    assert m.slug_page(rel) in pages, rel
    bad = []
    for f in (x for x in pages if x.endswith(".html")):
        s = open(os.path.join(SPEC, f), encoding="utf-8").read()
        assert 'id="q"' in s and (f == "index.html" or 'class="side"' in s)   # 搜索框；除首页外都有总目录
        for u in re.findall(r'(?:href|src)="([^"#]*)', s):
            if not u or u.startswith(("http:", "https:", "mailto:")):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(SPEC, urllib.parse.unquote(u.split("?")[0])))):
                bad.append((f, u))
    assert bad == []


def test_hub_serves_spec_directory(monkeypatch, tmp_path):
    """枢纽：/wqls/spec/ 给目录里的 index.html（不落到工作台单页应用），/wqls/spec 补斜杠；中文文件名能取"""
    pytest.importorskip("fastapi")
    import importlib

    from fastapi.testclient import TestClient
    d = tmp_path / "wqls" / "spec"
    d.mkdir(parents=True)
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("SPA", encoding="utf-8")
    (d / "index.html").write_text("SPEC", encoding="utf-8")
    (d / "G4-旋梭组.html").write_text("HOOK", encoding="utf-8")
    monkeypatch.setenv("WQ_HUB_NO_START", "1")
    monkeypatch.setenv("WQ_WEB_DIST", str(tmp_path))
    import hub.app as app_mod
    app_mod = importlib.reload(app_mod)
    try:
        c = TestClient(app_mod.app)
        assert c.get("/wqls/spec/").text == "SPEC"
        r = c.get("/wqls/spec", follow_redirects=False)
        assert r.status_code == 308 and r.headers["location"] == "/wqls/spec/"
        assert c.get("/wqls/spec/" + urllib.parse.quote("G4-旋梭组.html")).text == "HOOK"
        assert c.get("/process").text == "SPA"
    finally:
        monkeypatch.delenv("WQ_WEB_DIST")
        importlib.reload(app_mod)


WQLS = os.path.dirname(SPEC)


def test_lab_blocks_point_to_existing_pages():
    """说明书里的动画、虚拟实验、三维模型块（data-src）都指向存在的页面"""
    bad = []
    for f in (x for x in os.listdir(SPEC) if x.endswith(".html")):
        s = open(os.path.join(SPEC, f), encoding="utf-8").read()
        for u in re.findall(r'data-src="([^"]+)"', s):
            p = os.path.normpath(os.path.join(SPEC, u.split("?")[0]))
            if not os.path.exists(p):
                bad.append((f, u))
    assert bad == []
    home = open(os.path.join(SPEC, "index.html"), encoding="utf-8").read()
    assert 'class="hero"' in home and "proto=1" in home                 # 首页是整机虚拟样机


def test_proto_data_matches_design():
    """虚拟样机数据 proto.json 和设计一致：挑线机构是 G4/挑线机构.json 现在的，固件工作周期是 sim_sew.json 现在的"""
    import json
    pd = json.load(open(os.path.join(WQLS, "proto.json"), encoding="utf-8"))
    tk = json.load(open(os.path.join(ROOT, "docs", "设计", "WQ-LS", "G4", "挑线机构.json"), encoding="utf-8"))
    assert pd["takeup"]["new"] == json.loads(json.dumps(tk["lk"])) and pd["takeup"]["old"] == tk["previous_G4"], "重跑 tools/wqls/proto_web.py"
    sim = json.load(open(os.path.join(ROOT, "factory", "designs", "ctrl-ls", "fw", "out", "sim_sew.json"), encoding="utf-8"))
    for sc in sim["scenarios"]:
        if sc["id"] in pd["cycle"]["scenarios"]:
            a, b = pd["cycle"]["scenarios"][sc["id"]], sc["series"]
            assert a["state"] == b["state"] and all(abs(x - y) < 0.06 for x, y in zip(a["rpm"], b["rpm"])), "重跑 tools/wqls/proto_web.py"
    assert len(pd["assembly"]) >= 19 and all(s["ok"] for s in pd["assembly"])
    dyn = os.path.join(ROOT, "docs", "设计", "WQ-LS", "G8", "G8.1_动力学.json")
    if os.path.exists(dyn):                                              # 4.1 多体动力学：说明书里的数据是现在的结果
        assert pd.get("dyn41") and pd["dyn41"]["summary"] == json.load(open(dyn, encoding="utf-8")), "重跑 tools/wqls/proto_web.py"


def test_takeup_lab_matches_python():
    """挑线虚拟实验的网页算法（takeup-calc.js）和 Python（g81_takeup.takeup3d）逐项一致"""
    import shutil
    import subprocess
    if not shutil.which("node"):
        pytest.skip("没有 node")
    js = r"""
const fs=require('fs'),vm=require('vm'),path=require('path'),dir=process.argv[1];
const ctx={};vm.runInNewContext(fs.readFileSync(path.join(dir,'takeup-calc.js'),'utf8'),ctx);
const C=ctx.WQTakeup,TK=JSON.parse(fs.readFileSync(path.join(dir,'proto.json'),'utf8')).takeup;let w=0;
for(const n of ['new','old'])for(const f of Object.keys(TK.fabrics)){const r=C.takeup3d(TK[n],TK,f),p=TK.python[n][f];
 for(const k of ['margin','neg','pre','Smax'])w=Math.max(w,Math.abs(r[k]-p[k]));if(r.top!==p.top)w=99;}
console.log(w);"""
    out = subprocess.run(["node", "-e", js, WQLS], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert float(out.stdout.strip()) <= 0.01


def _labs():
    spec = importlib.util.spec_from_file_location("labs_web", os.path.join(ROOT, "tools", "wqls", "labs_web.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_labs_data_matches_design():
    """第 172b 轮第二批：互动块数据 labs.json、fea.bin、cast.bin 和设计结果一致（改了设计没重跑 tools/wqls/labs_web.py 就红）"""
    import json
    pytest.importorskip("numpy")
    L = json.load(open(os.path.join(WQLS, "labs.json"), encoding="utf-8"))
    m = _labs()
    hint = "重跑 python3 tools/wqls/labs_web.py <整机目录> <凝固仿真目录>"
    assert L["mech"] == json.loads(json.dumps(m.mech())), hint
    tq = json.loads(json.dumps(m.torque()))
    assert all(L["torque"][k] == tq[k] for k in tq), hint                   # 驱动力矩、振动力、曲柄销力都是 G2 dyn.py 现在的结果
    assert L["bom"] == json.loads(json.dumps(m.bom())) and L["clash"] == json.loads(json.dumps(m.clash())), hint
    nc = json.loads(json.dumps(m.nc()))
    assert {k: (v["t_total"], len(v["moves"]), v["src"]) for k, v in L["nc"].items()} == {k: (v["t_total"], len(v["moves"]), v["src"]) for k, v in nc.items()}, hint
    src = os.path.join(ROOT, "docs", "设计", "WQ-LS")
    fe = json.load(open(os.path.join(src, "G2", "有限元.json"), encoding="utf-8"))["stats"]
    assert L["fea"]["vm_max"] == fe["vm_max_mpa"] and L["fea"]["elements"] == fe["elements"], hint
    f = L["fea"]
    assert os.path.getsize(os.path.join(WQLS, "fea.bin")) == f["nv"] * 12 + f["nt"] * 6 + f["nv"] * 16
    for part, zh in (("upper", "上件"), ("lower", "下件")):
        cj = json.load(open(os.path.join(src, "G5", f"凝固仿真_{zh}.json"), encoding="utf-8"))
        c = L["cast"][part]
        assert c["variant"] == cj["variant"] and abs(c["t_end"] - cj["t_solid_total_s"]) < 0.06 and c["mass_kg"] == cj["mass_casting_kg"], hint
    assert os.path.getsize(os.path.join(WQLS, "cast.bin")) == sum(c["n"] * 9 for c in L["cast"].values())
    # 平衡：网页按 F = F0 + k·dF 算的最大振动力，和 G2 dyn.py 在这个 k 重算的一样
    import sys

    import numpy as np
    sys.path.insert(0, os.path.join(ROOT, "tools", "wqls"))
    import dyn
    T = L["torque"]
    for k in (0.0, 0.35, T["k_design"], 1.0):
        F = np.array(T["shake0"]).T + k * np.array(T["dshake"]).T
        ref = dyn.Machine(k=k).run()["F_shake"][::2]
        assert abs(np.hypot(*F.T).max() - np.hypot(*ref.T).max()) < 0.05
    assert len(L["inertia"]["parts"]) >= 5 and L["inertia"]["parts"]["needle_bar"]["Fmax"] > 100
