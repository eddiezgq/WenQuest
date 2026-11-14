# -*- coding: utf-8 -*-
"""第 138 轮 G7.1：问渠缝纫机厂里 WQ-LS 8 种变型的物料清单和设计一致（tools/wqls/g7_bom.py --check）。
设计一改（三维零件、物料号、选项），这条测试就失败：重跑 python3 tools/wqls/g7_bom.py 把工厂清单更新。"""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _mod():
    spec = importlib.util.spec_from_file_location("g7_bom", os.path.join(ROOT, "tools", "wqls", "g7_bom.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_wqls_bom_matches_design():
    m = _mod()
    assert m.check() == []
    b = m.build()
    assert len(b) == 8 and {"WQ-LS", "WQ-LS-TED"} <= set(b)
    ted = {ln["code"] for ln in b["WQ-LS-TED"]["lines"]}
    base = {ln["code"] for ln in b["WQ-LS"]["lines"]}
    assert {"LS-710", "BUY-STEP-42", "LS-301D"} <= ted and "LS-523" not in ted      # 剪线凸轮、步进电机、镀膜旋梭；E 去掉针距旋钮
    assert {"LS-523", "LS-301"} <= base and not base & {"LS-710", "BUY-STEP-42", "LS-301D"}
