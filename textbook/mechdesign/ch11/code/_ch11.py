"""第 11 章共用：WQ-CR5 大臂的疲劳——多体动力学的载荷历程、有限元的单位载荷工况、数字工厂的疲劳程序。

- 载荷历程：数字工厂“多体动力学”（cae/mbd.py）跑机器人厂的标准动作（wqcr5.RUNIN_POSES_DEG：初始位姿 → 两个位姿 → 回来，
  每段 1.2 s、段间停 0.3 s，带 5 kg 标准负载）。机器人厂的跑合台用五次多项式，“多体动力学”的驱动是梯形速度，本书用后者。
  读出“关节反力”通道 rf.link3、rm.link3（大臂对小臂一侧的力和力矩，世界坐标），换算成大臂 J3 端面上的载荷（零件坐标）；
  J3 模组装在大臂端部、属于大臂这个构件，它的重力和惯性力也压在端面上，一并计入（模组质心在 J3 中心，转动惯量略去）。
- 有限元：数字工厂“仿真与分析”的求解程序（cae/solve.py）。零件是 WQ-CR5 大臂示例零件，内角按 2 mm 圆角做（第 10 章 10.4 节），
  内角一圈局部加密。线弹性，叠加原理：六个单位载荷（Fx、Fy、Fz、Mx、My、Mz）各算一次，任一时刻的应力张量 = Σ 载荷分量 × 单位工况。
  J3 端的内角：J2 端面固定、J3 端面加载；J2 端（根部）的内角：反过来，J3 端面固定、J2 端面加平衡载荷。
- 疲劳：数字工厂的 cae/fatigue.py（pyLife 雨流、古德曼、迈因纳、海巴赫）。
重的计算（多体动力学 + 12 次有限元）结果缓存在临时目录，同一台机器上第二次运行直接读出（输入不变，结果相同）。
长度 mm，力 N，力矩 N·mm（对外多用 N·m），应力 MPa。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1]
for p in (BOOK / "ch10" / "code",):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import numpy as np  # noqa: E402

import _ch10 as H10  # noqa: E402
import _ch11fe as FE  # noqa: E402
from _ch11fe import (AL, FIL, HMIN, cycle, end_loads, frames, heavy, to_cart, to_cyl, unit_cases, tensor_at,  # noqa: E402,F401
                     arm_step, ball_mesh)
from bookout import COLORS, T  # noqa: E402
from cae import fatigue as FT, mbd, mbd_models as MM, solve as S, struct_parts as SP, wqcr5 as W  # noqa: E402,F401

INK, MUTED, ACC = COLORS["ink"], COLORS["muted"], COLORS["accent"]
mat = H10.mat
principal = H10.principal
vm_of = H10.vm_of
SHIFT_H, DAYS, YEARS = 16.0, 250, 5.0      # 两班、每年 250 天、5 年（本书设定的寿命要求）


def eig_all(h):
    """(..., 6) 的应力分量 → (..., 3) 主应力（从小到大），一次算完"""
    m = np.stack([np.stack([h[..., 0], h[..., 3], h[..., 5]], -1), np.stack([h[..., 3], h[..., 1], h[..., 4]], -1),
                  np.stack([h[..., 5], h[..., 4], h[..., 2]], -1)], -2)
    return np.linalg.eigvalsh(m)


def vm_all(w):
    return np.sqrt(0.5 * ((w[..., 0] - w[..., 1]) ** 2 + (w[..., 1] - w[..., 2]) ** 2 + (w[..., 2] - w[..., 0]) ** 2))


def signed_vm_all(w):
    """带符号的冯·米塞斯：符号取绝对值最大的那个主应力的符号"""
    v = vm_all(w)
    return np.where(np.abs(w[..., 2]) >= np.abs(w[..., 0]), v, -v)


def signed_vm(s6):
    return float(signed_vm_all(eig_all(np.asarray(s6, float))))


THETA = np.radians(np.arange(0, 360, 5))       # 圆周上每 5° 一排点


def field(U_end, L6, L0):
    """圆角表面全部点（72 个方位 × 一排）：静止伸直时的冯·米塞斯 vm0、节拍中的冯·米塞斯 vm(t)、带符号的 svm(t)、最大主应力 s1(t)、
    应力张量 h(t)。返回 dict，数组的第一维是点（方位优先）"""
    hs, h0s = [], []
    for th in THETA:
        hs.append(tensor_at(U_end, L6, th))
        h0s.append(tensor_at(U_end, L0[:, None], th)[:, 0, :])
    h = np.concatenate(hs)
    h0 = np.concatenate(h0s)
    w = eig_all(h)
    n = len(U_end["phi"])
    return {"h": h, "vm0": vm_all(eig_all(h0)), "vm": vm_all(w), "svm": signed_vm_all(w), "s1": w[..., 2],
            "theta": np.repeat(THETA, n), "phi": np.tile(np.asarray(U_end["phi"], float), len(THETA)),
            "k": np.tile(np.arange(n), len(THETA))}


def surface_axes(U_end, k, th, rf=FIL, end="J3"):
    """圆角表面点的三个方向：外法线 n（指向空腔）、沿圆角的切向 t1、环向 t2（直角坐标）"""
    p = SP.params_of("wqcr5_upper", None)
    ri = p["D"] / 2 - p["t"]
    zc = p["L"] - p["flange_t"] if end == "J3" else p["flange_t"]
    zf = zc + (-rf if end == "J3" else rf)
    r, z = U_end["rz"][k]
    er = np.array([math.cos(th), math.sin(th), 0.0])
    et = np.array([-math.sin(th), math.cos(th), 0.0])
    ez = np.array([0.0, 0.0, 1.0])
    nr, nz = (r - (ri - rf)) / rf, (z - zf) / rf          # 从圆心指向点：指向材料；空腔一侧是它的反方向
    n = -(nr * er + nz * ez)
    t1 = -nz * er + nr * ez
    return n, t1, et


def damage(series, surface="fine_turned", size_factor=0.85, kf=1.0, haibach=True, material=None):
    """用数字工厂的 fatigue.compute 算一个应力历程（MPa）每块的损伤；另给：最大一个循环的古德曼等效应力幅 sa_eq、
    疲劳安全系数 S = S_D / sa_eq、损伤等效应力幅 s_de（每块同样多次数的等幅循环、损伤相同的应力幅）"""
    m = material or AL
    _, summ = FT.compute([1.0], 1.0, list(series), 1.0, m, surface, size_factor, kf, haibach)
    D = summ["damage_per_block"]
    sa_eq = summ["hot_cycles"][0]["sigma_a_eq"] if summ["hot_cycles"] else 0.0
    n = max(summ["cycles_per_block"], 1)
    s_de = 0.0
    if D > 0:
        import pandas as pd
        import pylife.materiallaws  # noqa: F401
        wc = pd.Series({"SD": summ["S_D"], "ND": float(m["N_D"]), "k_1": float(m["k"]),
                        "k_2": (2 * m["k"] - 1) if haibach else np.inf}).woehler
        s_de = float(np.asarray(wc.load(np.array([n / D])))[0])
    return D, dict(summ, sa_eq=sa_eq, S_fat=(summ["S_D"] / sa_eq) if sa_eq > 0 else math.inf, s_de=s_de, n=n)


def directions(n=60):
    """半球上大致均匀的 n 个方向（斐波那契点），临界平面法用"""
    k = np.arange(n) + 0.5
    phi = np.arccos(1 - k / n)
    th = math.pi * (1 + 5 ** 0.5) * k
    return np.c_[np.sin(phi) * np.cos(th), np.sin(phi) * np.sin(th), np.cos(phi)]


def normal_stress(hist, d):
    """(时间, 6) 的应力历程在法向 d 的面上的正应力"""
    sxx, syy, szz, sxy, syz, szx = (hist[:, i] for i in range(6))
    x, y, z = d
    return sxx * x * x + syy * y * y + szz * z * z + 2 * (sxy * x * y + syz * y * z + szx * z * x)


def proxy(arr):
    """一个重复块里最大的雨流循环就是全程的最大值到最小值：σa = 变程 / 2，σm = 中值；返回古德曼等效应力幅
    （与 fatigue.compute 相同，取 |σm|）。用来在几千个点、几十个面里先找出最危险的，再用 fatigue.compute 细算"""
    sa = np.ptp(arr, axis=-1) / 2
    sm = (arr.max(axis=-1) + arr.min(axis=-1)) / 2
    return sa / (1 - np.clip(np.abs(sm) / AL["ultimate_mpa"], 0, 0.999))


def critical_plane(U_end, F, end, step_deg=5):
    """临界平面：每个表面点、垂直于表面每 step_deg 一个面上的正应力，最大一个循环的古德曼等效应力幅最大的那个点和面。
    返回 (点号, 面的法向, 夹角（从圆角切向量起）°, 正应力历程)"""
    als = np.radians(np.arange(0, 180, step_deg))
    best = (-1.0, -1, -1, None)
    for i in range(len(F["vm0"])):
        _, t1, t2 = surface_axes(U_end, int(F["k"][i]), float(F["theta"][i]), end=end)
        dirs = np.cos(als)[:, None] * t1 + np.sin(als)[:, None] * t2
        pr = proxy(np.stack([normal_stress(F["h"][i], d_) for d_ in dirs]))
        k = int(np.argmax(pr))
        if pr[k] > best[0]:
            best = (float(pr[k]), i, k, dirs[k])
    return best[1], best[3], float(np.degrees(als[best[2]])), normal_stress(F["h"][best[1]], best[3])


def lam_for_life(series_fn, n_blocks, haibach=True):
    """二分：损伤在 n_blocks 个块里刚好为 1 的载荷放大倍数 λ；series_fn(λ) 给出放大后的应力历程"""
    lo, hi = 1.0, 100.0
    for _ in range(60):
        mid = math.sqrt(lo * hi)
        D, _ = damage(series_fn(mid), haibach=haibach)
        if D * n_blocks > 1:
            hi = mid
        else:
            lo = mid
    return math.sqrt(lo * hi)


def cycles_per_life(block_s):
    return SHIFT_H * 3600 * DAYS * YEARS / block_s
