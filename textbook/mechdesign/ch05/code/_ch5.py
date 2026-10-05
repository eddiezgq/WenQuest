"""第 5 章共用：材料数据。

- 数字工厂材料库（factory/digital/cae/materials.py，12 种、逐条出处）——经 conventions/mdstd.py 读取；
- 库里没有的材料：本书数字化表 std/ashby_materials.yaml（典型值，待核对）；
- 国标试样性能：std/steel_grades.yaml；牌号对照：std/grade_xref.yaml。
单位：E 用 GPa，强度 MPa，密度 g/cm³。
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (ROOT / "factory" / "digital", HERE.parents[1] / "conventions", HERE.parents[1] / "ch33" / "code"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import mdstd                            # noqa: E402
from bookout import COLORS, T           # noqa: E402

INK, MUTED, ACC = COLORS["ink"], COLORS["muted"], COLORS["accent"]
CLS_COLOR = {"metal": "#1f77b4", "composite": "#2ca02c", "polymer": "#ff7f0e", "natural": "#8c564b", "ceramic": "#9467bd"}
CLS_NAME = {"metal": T("金属", "metals"), "composite": T("复合材料", "composites"), "polymer": T("塑料", "polymers"),
            "natural": T("天然材料", "natural"), "ceramic": T("陶瓷", "ceramics")}


def lib(mid: str) -> dict:
    """材料库的一种材料：E（GPa）、rho、sy、sb、s1（MPa）"""
    m = mdstd.material(mid)
    return {"id": mid, "name": m["name"], "E": m["E"] / 1000, "rho": m["density"], "sy": m["sigma_s"], "sb": m["sigma_b"],
            "s1": m["sigma_1"], "note": m["note"], "src": m["src"]}


def materials() -> list[dict]:
    """选材用的材料清单：材料库里有的用库里的值，其余用 std/ashby_materials.yaml。"""
    t = mdstd.table("ashby_materials")
    out = []
    for r in t["rows"]:
        d = dict(zip(t["columns"], r))
        name = T(d["zh"], d["en"])
        if d["lib"]:
            m = lib(d["lib"])
            out.append({"id": d["id"], "name": name, "cls": d["cls"], "E": m["E"], "rho": m["rho"],
                        "sy": m["sy"] if m["sy"] else m["sb"], "src": T("数字工厂材料库", "factory material library")})
        else:
            out.append({"id": d["id"], "name": name, "cls": d["cls"], "E": d["E"], "rho": d["rho"], "sy": d["sy"],
                        "src": T("典型值（待核对）", "typical value (to be checked)")})
    return out


def by_id(mid: str) -> dict:
    return next(m for m in materials() if m["id"] == mid)


def steel_grades() -> list[dict]:
    t = mdstd.table("steel_grades")
    return [dict(zip(t["columns"], r)) for r in t["rows"]]
