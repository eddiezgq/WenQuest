"""第 4 章共用：公差带、配合的计算与画图小工具，以及本章用到的几组数据。

数据来源：
- SH-301 B 版的直径、长度、公差带取第 33 章（ch33/code/_shaft.py）；
- 轴承 6207、6010 的尺寸与公差取本书数字化标准表（GB/T 276、GB/T 307.1 / ISO 492）；
- 标准公差、基本偏差取本书数字化标准表（GB/T 1800.1 / ISO 286-1），经 conventions/mdstd.py 读取；
- 磨削尺寸的分布、三坐标检验特性取数字工厂的测量模型（factory/digital/sim/errors.py、sim/engine.py 的砂轮磨损）；
- 过程能力的算法取数字工厂质量模块（factory/digital/hub/spc.py）。
单位：尺寸 mm，偏差 μm（函数名或注释里写明）。
"""
from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for p in (ROOT / "factory" / "digital", HERE.parents[1] / "conventions", HERE.parents[1] / "ch33" / "code"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import _shaft as S                      # noqa: E402
import mdstd                            # noqa: E402
from bookout import COLORS, T           # noqa: E402
from hub import spc                     # noqa: E402
from sim import engine as ENG           # noqa: E402
from sim import errors as ERR           # noqa: E402

INK, MUTED, ACC = COLORS["ink"], COLORS["muted"], COLORS["accent"]
C_HOLE, C_SHAFT, C_BRG = "#2c6fbb", "#c0392b", "#7a868d"

BRG = mdstd.bearing(S.BRG)              # 6207：d 35，D 72，B 17
BRG_TOL = mdstd.bearing_tol(BRG["d"], BRG["D"])


# ---------------------------------------------------------------- 公差带
def zone(d: float, code: str) -> tuple[float, float]:
    """公差带代号（'k6'、'H7'、'G7' …）→ (下极限偏差, 上极限偏差)，μm。小写是轴，大写是孔。"""
    m = re.fullmatch(r"([a-zA-Z]+)(\d+)", code)
    letter, grade = m.group(1), int(m.group(2))
    if letter.islower():
        es, ei = mdstd.shaft_dev(letter, grade, d)
    else:
        es, ei = mdstd.hole_dev(letter, grade, d)
    return float(ei), float(es)


def fit(hole: tuple[float, float], shaft: tuple[float, float]) -> dict:
    """孔、轴的偏差带（μm）→ 最大间隙、最小间隙（负值为过盈）、配合公差与配合的种类。"""
    Xmax = hole[1] - shaft[0]
    Xmin = hole[0] - shaft[1]
    kind = "clearance" if Xmin >= 0 else "interference" if Xmax <= 0 else "transition"
    return {"Xmax": Xmax, "Xmin": Xmin, "Tf": Xmax - Xmin, "kind": kind,
            "Ymax": -Xmin, "Ymin": -Xmax}


KIND_ZH = {"clearance": T("间隙配合", "clearance fit"), "interference": T("过盈配合", "interference fit"),
           "transition": T("过渡配合", "transition fit")}


def draw_zone(ax, x, w, lo, hi, color, label=None, hatch=None):
    """在公差带图上画一个带：x 是左边位置，w 宽度，lo/hi 偏差（μm）。"""
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((x, lo), w, hi - lo, fc=color, ec=color, alpha=0.30 if hatch is None else 0.12, lw=0.8, hatch=hatch))
    ax.add_patch(Rectangle((x, lo), w, hi - lo, fc="none", ec=color, lw=0.9))
    if label:
        ax.text(x + w / 2, hi + 1.0, label, ha="center", va="bottom", fontsize=7, color=color)


# ---------------------------------------------------------------- 数字工厂：磨床磨轴承位的尺寸
GRD_WEAR = ENG.WEAR_PER_PART["grd-01"]  # 每件砂轮磨损 1/30
GRD_RESET = 0.08                        # 剩余寿命低于 0.08 时修整砂轮（sim/engine.py）
SLOPE = 0.0125                          # 砂轮磨损从 0 到 1 时轴承位直径增大 0.0125 mm（sim/errors.py）
BASE_D35 = 35.0065                      # 新修整砂轮磨出的平均直径（sim/errors.py）
SD_D35 = 0.0012                         # 重复性（标准差）


def wear_sequence(n: int) -> list[float]:
    """数字工厂磨床连续磨 n 件时每件的砂轮磨损（0 → 修整 → 0 …），与 sim/engine.py 相同。"""
    life, seq = 1.0, []
    for _ in range(n):
        seq.append(1 - life)
        life = max(0.0, life - GRD_WEAR)
        if life < GRD_RESET:
            life = 1.0
    return seq


class _Part:
    def __init__(self, wear):
        self.grind_wear = wear
        self.err = {}


def inspect_batch(n: int, seed: int = 4, problems: dict | None = None) -> list[list[tuple]]:
    """用数字工厂的测量模型生成 n 根 SH-301 的三坐标检验记录（每根一行：[(代号, 名称, 名义, 下限, 上限, 测得值)]）。
    problems = {情景: 大小}：老师注入的工艺问题（sim/errors.py 的 PROBLEMS），None 为正常状态。"""
    em = ERR.ErrorModel(seed=seed)
    for p, mag in (problems or {}).items():
        em.inject(p, mag)
    main = random.Random(seed)
    rows = []
    for w in wear_sequence(n):
        part = _Part(w)
        em.on_process("grd-01", part, w)
        em.on_process("key-01", part, 0.0)
        rows.append(em.measure(part, main))
    return rows


CHARS = ERR.CHARS
