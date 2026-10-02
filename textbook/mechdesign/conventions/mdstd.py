"""《机械设计》的数字化标准表（第 11 轮第 4 步）。

书里的程序、虚拟实验和工程任务单都从这里取标准数据，不在程序里手抄数字。每个函数返回数值，同时可以用
``cite(...)`` 取得出处（标准号 + 表号），写进计算书。

    from mdstd import it, shaft_dev, fit_limits, key_for, bearing, material, surface_factor, size_factor
    lo, hi = fit_limits(35, "k6")          # (35.002, 35.018)
    k = key_for(40)                        # {'b': 12, 'h': 8, 't': 5.0, 't1': 3.3, ...}

表放在 textbook/mechdesign/std/*.yaml；材料与数字工厂有限元服务的材料库同源（factory/digital/cae/materials.py）。
"""
from __future__ import annotations

import functools
import importlib.util
import math
import re
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
STD = HERE.parent / "std"
ROOT = HERE.parents[2]
MPA_PER_KPSI = 6.894757


@functools.lru_cache(maxsize=None)
def table(name: str) -> dict:
    return yaml.safe_load((STD / f"{name}.yaml").read_text(encoding="utf-8"))


def cite(name: str) -> str:
    """标准号 + 表号，写进计算书的“出处”一栏。"""
    t = table(name)
    s = t.get("standard")
    if s:
        return f"{s['code']} {s.get('table', '')}".strip()
    return t.get("source") or t.get("title", name)


def _row(name: str, d: float) -> dict:
    t = table(name)
    cols = t["columns"]
    for r in t["rows"]:
        row = dict(zip(cols, r))
        if row["over_mm"] < d <= row["to_mm"] or (row["over_mm"] == 0 and d == 0):
            return row
    raise ValueError(f"{name}: 公称尺寸 {d} mm 超出表的范围")


# ---------------------------------------------------------------- 极限与配合（GB/T 1800.1 / ISO 286-1）

def it(grade: int, d: float) -> int:
    """标准公差 ITgrade（μm）。"""
    return _row("iso286_it", d)[f"IT{grade}"]


def shaft_dev(letter: str, grade: int, d: float) -> tuple[int, int]:
    """轴的 (es, ei)，μm。"""
    row = _row("iso286_shaft", d)
    T = it(grade, d)
    if letter in ("f", "g", "h"):
        es = row[letter]
        return es, es - T
    if letter == "js":
        return T / 2, -T / 2
    if letter == "k" and not 4 <= grade <= 7:
        raise ValueError("k 的基本偏差表只录入了 IT4–IT7")
    ei = row[letter]
    return ei + T, ei


def hole_dev(letter: str, grade: int, d: float) -> tuple[int, int]:
    """孔的 (ES, EI)，μm：只录入 H、JS、N9、P9。"""
    T = it(grade, d)
    if letter == "H":
        return T, 0
    if letter == "JS":
        return T / 2, -T / 2
    if letter == "N" and grade == 9:
        return 0, -T
    if letter == "P" and grade == 9:
        es = _row("iso286_hole", d)["P9_ES"]
        return es, es - T
    raise ValueError(f"孔的基本偏差 {letter}{grade} 尚未录入")


def fit_limits(d: float, code: str) -> tuple[float, float]:
    """公差带代号（如 'k6'、'H7'、'N9'）→ (最小极限尺寸, 最大极限尺寸)，mm。"""
    m = re.fullmatch(r"([a-zA-Z]+)(\d+)", code)
    letter, grade = m.group(1), int(m.group(2))
    hi, lo = (hole_dev if letter[0].isupper() else shaft_dev)(letter, grade, d)
    return round(d + lo / 1000, 4), round(d + hi / 1000, 4)


# ---------------------------------------------------------------- 平键（GB/T 1095 / 1096）

def key_for(d: float) -> dict:
    row = _row("gbt1095_key", d)
    return {k: row[k] for k in ("b", "h", "t", "t1")} | {"d_range": (row["over_mm"], row["to_mm"])}


def key_length(L_max: float) -> int:
    """不超过 L_max 的最大标准键长。"""
    return max(x for x in table("gbt1095_key")["lengths"] if x <= L_max)


# ---------------------------------------------------------------- 滚动轴承

def bearing(code: str) -> dict:
    t = table("gbt276_6200")
    for r in t["rows"]:
        row = dict(zip(t["columns"], r))
        if row["code"] == code:
            return row
    raise ValueError(f"轴承 {code} 不在表中")


# ---------------------------------------------------------------- 材料（与数字工厂同源）

@functools.lru_cache(maxsize=None)
def _factory_materials():
    spec = importlib.util.spec_from_file_location("wq_cae_materials", ROOT / "factory" / "digital" / "cae" / "materials.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def material(mid: str) -> dict:
    """材料性能（MPa）：sigma_b, sigma_s, sigma_1 (σ₋₁), tau_1 (τ₋₁), E, mu；src 为出处。"""
    mod = _factory_materials()
    m = mod.BY_ID[mid]
    return {"id": mid, "name": m["name"], "sigma_b": m["ultimate_mpa"], "sigma_s": m["yield_mpa"],
            "sigma_1": m["sigma_1"], "tau_1": m["tau_1"], "E": m["E_mpa"], "mu": m["nu"], "density": m["density"],
            "N0": m["N_D"], "m": m["k"], "note": m["note"], "src": "；".join(mod.SRC[k] for k in m["src"])}


# ---------------------------------------------------------------- 疲劳修正系数

def surface_factor(finish: str, sigma_b: float) -> float:
    """表面质量系数 β（[SHI] 的 k_a = a·σ_b^b）。finish: ground / machined / hot_rolled / forged。"""
    c = table("fatigue_factors")["surface_factor"]["rows"][finish]
    return c["a"] * sigma_b ** c["b"]


def size_factor(d: float) -> float:
    """尺寸系数 ε（旋转弯曲与扭转；[SHI] 的 k_b）。"""
    for r in table("fatigue_factors")["size_factor"]["ranges"]:
        if r["d_min"] <= d <= r["d_max"]:
            return r["c"] * d ** r["e"]
    raise ValueError(f"尺寸系数公式不适用于 d = {d} mm")


def notch_sensitivity(r: float, sigma_b: float, torsion: bool = False) -> float:
    """缺口敏感系数 q（钢），r 为缺口圆角半径 mm。"""
    c = table("fatigue_factors")["notch_sensitivity"]["torsion_sqrt_a_inch" if torsion else "bending_sqrt_a_inch"]
    S = sigma_b / MPA_PER_KPSI
    sqrt_a_mm = sum(ci * S ** i for i, ci in enumerate(c)) * math.sqrt(25.4)     # √in → √mm
    return 1.0 / (1.0 + sqrt_a_mm / math.sqrt(r))


def kt_estimate(kind: str) -> dict:
    return table("fatigue_factors")["kt_first_iteration"]["rows"][kind]
