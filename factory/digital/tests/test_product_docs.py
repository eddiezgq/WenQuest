# -*- coding: utf-8 -*-
"""第 181 轮：WQ-LS 设计说明书入口——案例 C 第 5 步最上面是设计说明书主入口；
首页“本厂产品资料”只在缝纫机厂出现（PRODUCT_DOCS 按厂 id 查，减速器厂没有）。"""
import os
import re

import yaml

DIG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAC = os.path.dirname(DIG)
HOME = os.path.join(DIG, "web", "src", "pages", "Home.vue")
STEP5 = os.path.join(FAC, "cases", "sewing", "C", "5_三维与图纸.md")


def test_step5_main_entry_is_spec():
    lines = [l for l in open(STEP5, encoding="utf-8").read().splitlines() if l.strip()]
    assert lines[0].startswith("# ")
    # 标题下第一行：引用块里加粗的设计说明书链接（案例页把它画成主入口框）
    assert re.match(r"^> \*\*\[[^\]]*设计说明书[^\]]*\]\(/wqls/spec/\)\*\*$", lines[1]), lines[1]
    links = re.findall(r"\]\((/wqls/[^)]*)\)", open(STEP5, encoding="utf-8").read())
    assert links == ["/wqls/spec/", "/wqls/index.html?opt=TED"]          # 两个链接各一次，说明书在前


def _product_docs():
    src = open(HOME, encoding="utf-8").read()
    m = re.search(r"const PRODUCT_DOCS = \{(.*?)\n\};", src, re.S)
    assert m, "Home.vue 里没有 PRODUCT_DOCS"
    return src, dict(re.findall(r"'([a-z-]+)': \[(.*?)\],?\n", m.group(1) + "\n"))


def test_home_docs_only_for_sewing():
    src, docs = _product_docs()
    assert list(docs) == ["wenquest-sewing"]                              # 减速器厂等别的厂不显示
    plant = yaml.safe_load(open(os.path.join(FAC, "plants", "wenquest-sewing.yaml"), encoding="utf-8"))
    assert plant["id"] == "wenquest-sewing"                               # 和工厂清单的 id 对得上
    row = docs["wenquest-sewing"]
    for u in ("'/wqls/spec/'", "'/wqls/index.html?opt=TED'", "'/cases/C'"):
        assert u in row
    assert 'v-if="docs.length"' in src                                    # 没有资料的厂整张卡不出
    assert "PRODUCT_DOCS[session.config?.plant?.id]" in src
