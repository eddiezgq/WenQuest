"""第 10 章共用：调用数字工厂“仿真与分析”（问渠 CAE）的同一套几何与求解程序，再从节点应力张量算各种强度理论。

- 有限元：factory/digital/cae/solve.py（gmsh 二阶四面体 + CalculiX 线性静力），网页上点“计算”用的就是它；
  CAE 只把冯·米塞斯应力交给网页，本章还要主应力和特雷斯卡应力，所以在读结果文件时把六个应力分量一并留下（`fe_solve`）。
- 零件：WQ-CR5 大臂（CAE 示例零件 wqcr5_upper，struct_parts.py；预设载荷取机器人厂原件 wqcr5.py）；其余几何在各程序里用 gmsh 现做。
- 材料：数字工厂材料库（cae/materials.py，与 mdstd 同源）。
网格单线程、直接求解器，数字每次相同。长度 mm，力 N，应力 MPa。
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

os.environ.setdefault("WQ_MESH_THREADS", "1")
os.environ.setdefault("WQ_CCX_SOLVER", "SPOOLES")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1]
ROOT = HERE.parents[3]
CAE = ROOT / "factory" / "digital" / "cae"
for p in (CAE.parent, BOOK / "conventions", BOOK / "ch07" / "code", BOOK / "ch08" / "code", BOOK / "ch33" / "code"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from cae import geometry as GEO, materials as MT, solve as S, struct_parts as SP  # noqa: E402
from bookout import COLORS, T  # noqa: E402

INK, MUTED, ACC = COLORS["ink"], COLORS["muted"], COLORS["accent"]


def mat(mid):
    return MT.get(mid)


# ---------------------------------------------------------------- 有限元：同一套 CAE 程序，多留下应力张量
def fe_solve(step, loads, size_mm, material):
    """返回 (统计, 表面结果, 节点坐标 {id: xyz}, 节点应力张量 {id: [sxx, syy, szz, sxy, syz, szx]})"""
    keep = {}
    orig = S.read_frd

    def grab(path):
        d, s = orig(path)
        keep["stress"] = s
        return d, s
    S.read_frd = grab
    try:
        st, surf, allv = S.solve(step, {"material": material, "loads": loads, "mesh": {"size_mm": size_mm}})
    finally:
        S.read_frd = orig
    return st, surf, allv["nodes"], keep["stress"]


def faces_of(step):
    f, _, _ = GEO.faces(step)
    return f


# ---------------------------------------------------------------- 应力状态与强度理论
def principal(s6):
    sxx, syy, szz, sxy, syz, szx = s6[:6]
    A = np.array([[sxx, sxy, szx], [sxy, syy, syz], [szx, syz, szz]])
    w = np.linalg.eigvalsh(A)
    return w[2], w[1], w[0]                              # σ1 ≥ σ2 ≥ σ3


def vm_of(p):
    s1, s2, s3 = p
    return math.sqrt(0.5 * ((s1 - s2) ** 2 + (s2 - s3) ** 2 + (s3 - s1) ** 2))


def tresca_of(p):
    return p[0] - p[2]


def cm_factor(p, st, sc):
    """库仑–莫尔（拉伸强度 st、压缩强度 sc，取正值）的安全系数"""
    s1, _, s3 = p
    if s3 >= 0:
        return st / s1 if s1 > 0 else math.inf
    if s1 <= 0:
        return sc / -s3
    return 1.0 / (s1 / st - s3 / sc)


def rankine_factor(p, st, sc):
    s1, _, s3 = p
    return min(st / s1 if s1 > 0 else math.inf, sc / -s3 if s3 < 0 else math.inf)


def away_from(nodes, P, constrained_pts, dist):
    """离约束面 dist 以外的节点（圣维南：约束附近的应力受边界条件影响，CAE 评估最大应力时也这样排除）"""
    from scipy.spatial import cKDTree
    ids = np.array(sorted(nodes))
    xyz = np.array([P[int(i)] for i in ids])
    d, _ = cKDTree(np.asarray(constrained_pts)).query(xyz)
    return ids[d > dist]


# ---------------------------------------------------------------- WQ-CR5 大臂（CAE 示例零件）
def upper_arm(params=None, scale=1.0):
    """返回 (参数, STEP, 面清单, 载荷, 示例信息)。scale：把预设载荷（伸直、5 kg 静载）乘一个系数"""
    p = SP.params_of("wqcr5_upper", params)
    step = SP.build("wqcr5_upper", p)
    faces = faces_of(step)
    ex = SP.example("wqcr5_upper", p, faces)
    R = ex["rows"]
    loads = [{"type": "fixed", "faces": R[0]["faces"]},
             {"type": "force", "faces": R[1]["faces"], "vector_n": [scale * R[1]["fx"], scale * R[1]["fy"], scale * R[1]["fz"]]},
             {"type": "moment", "faces": R[2]["faces"], "vector_nmm": [scale * R[2]["mx"] * 1e3, scale * R[2]["my"] * 1e3, scale * R[2]["mz"] * 1e3]}]
    return p, step, faces, loads, ex
