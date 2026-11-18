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
        assert 'class="side"' in s and 'id="q"' in s                       # 总目录、搜索框
        for u in re.findall(r'(?:href|src)="([^"#]*)', s):
            if not u or u.startswith(("http:", "https:", "mailto:")):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(SPEC, urllib.parse.unquote(u)))):
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
