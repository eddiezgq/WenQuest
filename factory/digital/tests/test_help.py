# -*- coding: utf-8 -*-
"""第 19 轮 J-8 ~ J-10：帮助在网页里读（副本与原件一致、每份都能转成网页、页面右上角“帮助”指向存在的文件）；
术语表守住叫法（“不再用”的词不出现在网页上）；导航分组与旧地址跳转。"""
import importlib.util
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
DIGITAL = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(DIGITAL))
WEB = os.path.join(DIGITAL, "web", "src")


def _sync():
    spec = importlib.util.spec_from_file_location("help_sync", os.path.join(DIGITAL, "help", "sync.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_copies_match_originals():
    """digital/help 里是 docs/帮助、docs/演示 的副本：改原件后要运行 help/sync.py"""
    m = _sync()
    if not os.path.isdir(os.path.join(REPO, "docs", "帮助")):
        pytest.skip("不在完整仓库里（只有 factory/）")
    for src, dst in m.FILES.items():
        assert src.exists(), "原件不存在：{}".format(src)
        assert dst.exists(), "副本不存在：{}（运行 python3 factory/digital/help/sync.py）".format(dst.name)
        assert src.read_text(encoding="utf-8") == dst.read_text(encoding="utf-8"), "{} 与原件不一致（运行 help/sync.py）".format(dst.name)


def test_every_help_renders_and_links():
    pytest.importorskip("markdown")
    from hub import help_api as HA
    groups = HA.listing()
    names = [i["name"] for g in groups for i in g["items"]]
    assert {"使用说明", "两周情景", "数字工厂术语表", "厂情中枢", "经营与财务", "学校版演示脚本", "企业版演示脚本", "演示前检查表"} <= set(names)
    for n in names:
        with open(HA.path_of(n), encoding="utf-8") as f:
            html = HA.render(f.read())
        assert "<h1" in html and "<table" in html or "<h1" in html, n
    html = HA.render("见[两周情景](两周情景.md)和[术语](数字工厂术语表.md#一工厂与时间)")
    assert 'href="/help/两周情景"' in html and 'href="/help/数字工厂术语表#' in html
    assert HA.path_of("../app") is None and HA.path_of("没有这份") is None


def test_index_links_point_to_existing_help():
    from hub import help_api as HA
    with open(HA.INDEX, encoding="utf-8") as f:
        md = f.read()
    for name in re.findall(r"\]\(([^)/#]+)\.md\)", md):
        assert HA.path_of(name), "总目录链接到不存在的帮助：" + name


def test_page_help_button_targets_exist():
    from hub import help_api as HA
    with open(os.path.join(WEB, "App.vue"), encoding="utf-8") as f:
        src = f.read()
    block = src[src.index("const HELP = ["):src.index("const helpName")]
    names = re.findall(r"\['/[^']*', '([^']+)'\]", block)
    assert len(names) >= 15
    for n in set(names) | {"使用说明"}:
        assert HA.path_of(n), "页面帮助指向不存在的文件：" + n


def _banned():
    with open(os.path.join(DIGITAL, "help", "数字工厂术语表.md"), encoding="utf-8") as f:
        md = f.read()
    out = set()
    for line in md.splitlines():
        if line.startswith("|") and not line.startswith("| ---") and "不再用" not in line:
            last = line.strip().strip("|").split("|")[-1].strip()
            out |= {w.strip() for w in last.split("、") if w.strip()}
    return out


def _visible(text):
    """去掉注释：HTML 注释、/* */、整行和行尾的 // 注释（网页上看不到的不算）"""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(re.sub(r"(^|\s)//.*$", "", line) for line in text.splitlines())


def test_glossary_banned_words_not_on_pages():
    banned = _banned()
    assert {"预案", "经营与成本", "仿真时间", "制造故障", "告警"} <= banned
    hits = []
    for root, _, files in os.walk(WEB):
        for fn in files:
            if fn.endswith((".vue", ".js")):
                p = os.path.join(root, fn)
                with open(p, encoding="utf-8") as f:
                    t = _visible(f.read())
                for w in banned:
                    if w in t:
                        hits.append("{}：{}".format(os.path.relpath(p, WEB), w))
    assert not hits, "页面上出现了术语表里“不再用”的词：" + "；".join(hits)


def test_nav_groups_and_old_routes():
    with open(os.path.join(WEB, "App.vue"), encoding="utf-8") as f:
        app = f.read()
    for g in ("总览", "从订单到回款", "保障", "设计与工艺", "教学", "资源"):
        assert "title: '{}'".format(g) in app
    assert "实验 15 · 任务" not in app and "'/labs'" in app and "'/director'" in app
    with open(os.path.join(WEB, "main.js"), encoding="utf-8") as f:
        routes = f.read()
    assert "{ path: '/work/manager', redirect: { path: '/finance', query: { tab: 'production' } } }" in routes
    for n in [7] + list(range(15, 24)):
        assert ("'/teach'" if n == 7 else "'/lab{}'".format(n)) in routes
    assert not os.path.exists(os.path.join(WEB, "pages", "Manager.vue"))
