"""《机械制造技术》的工艺计算书（第 13 轮第 4 步）。

计算书本身用《机械设计》的 CalcSheet（`textbook/mechdesign/conventions/calcsheet.py`：已知 → 求 → 计算 → 校核与结论，
导出 Word，也能导出发给学生的空白模板）——两本书、数字工厂共用一份，不另做一套。本模块只加两件事：

- lookup：从带逐行出处的数字化工艺数据表（`textbook/mfgtech/std/`，读表用 `textbook/tools/stdtab.py`）查值，
  出处（标准号 + 表号 + 数据出处）自动写进计算书；
- missing：列出一份计算书缺的项，AI 工艺评审员和自动测试用。

    from mfgcalc import CalcSheet, lookup
    cs = CalcSheet("SH-301 φ35k6 轴承位工序尺寸", item="SH-301")
    it7 = lookup(cs, "IT7", "it_grades", dict(size_over_mm__lt=35, size_to_mm__ge=35), "IT7_um", "μm", "精车工序公差")
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[2] / "tools"))
sys.path.insert(0, str(_HERE.parents[2] / "mechdesign" / "conventions"))

import stdtab  # noqa: E402
from calcsheet import CalcSheet  # noqa: E402,F401


def lookup(cs: "CalcSheet", sym: str, table: str, where: dict, col: str, unit: str, what: str = ""):
    """Value from a digitized table, recorded in the sheet with its standard, table and data source."""
    t = stdtab.table(table)
    row = t.find(**where)
    v = t.value(row, col)
    cs.table_value(sym, v, unit, what or f"{t.columns[col]['zh']}（{row.get('key')}）", t.cite(row))
    return v


def missing(cs: "CalcSheet", en: bool = False) -> list[str]:
    """What a complete calculation sheet lacks: givens, what to find, calculation steps, checks; every looked-up value cited."""
    msg = (("缺少“已知”", "缺少“求”", "缺少计算步骤", "缺少校核", "查表值没有注明出处") if not en else
           ("no givens", "nothing to find", "no calculation steps", "no checks", "a looked-up value has no source"))
    out = []
    if not any(r["kind"] == "given" for r in cs.rows):
        out.append(msg[0])
    if not cs.finds:
        out.append(msg[1])
    if not any(r["kind"] == "step" for r in cs.rows):
        out.append(msg[2])
    if not cs.checks:
        out.append(msg[3])
    if any(r["kind"] == "step" and r.get("formula") == "查表" and not r.get("src") for r in cs.rows):
        out.append(msg[4])
    return out
