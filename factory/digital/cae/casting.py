# -*- coding: utf-8 -*-
"""铸件凝固仿真（第 138 轮 G5.1）：体素（规则网格）有限差分 + 焓法，铸件、砂型、砂芯、冷铁一起算。

为什么用体素而不用 cae/thermal.py 的四面体有限元：铸件加上整块砂型、冒口、浇道一起划四面体网格，在机壳这种细节多的
铸件上划分失败；铸造仿真软件里体素有限差分也是常用做法（网格规则，铸件、砂型、冷铁按体素标材料）。

物理模型
- 导热：∂H/∂t = ∇·(k∇T)，显式时间推进；相邻两格的导热系数取调和平均（界面处自然处理砂—铁、铁—冷铁）。
- 焓法计入结晶潜热：H(T) 分段线性。灰铸铁按两段放热：液相线 TL → 共晶 TE + 5 放 f_pro 的潜热（初生奥氏体），
  共晶 TE + 5 → TE − 5 放其余（共晶平台）。固相分数 fs 由焓反算。
- 浇满瞬间开始冷却（不算充型）：铸件、冒口、浇道是浇注温度，砂型、冷铁是室温。外边界绝热（砂箱外层离铸件够远）。
- 结果：每一格凝固完的时间 t_sol；按 Chvorinov 规律 t = B·M² 换成“热模数” M（B 由同一程序算平板标定）。
- 孤立液相（补缩分析）：每隔一段时间，把还没凝固到 fs_crit 的铸件格子按连通区域分组；凡是和冒口（或浇注系统）不连通、
  后来自己凝固完的区域，就是孤立热节，体积和位置记下来，是缩孔、缩松的危险区。

单位：长度 m（输入可以 mm，函数里注明），时间 s，温度 ℃，k W/(m·K)，ρ kg/m³，cp J/(kg·K)，潜热 J/kg。
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import ndimage

# 材料（常见取值；灰铸铁的 TL、TE 按 HT250 碳当量约 3.9 的亚共晶成分）
MATERIALS = {
    "HT250": dict(k=40.0, rho=7000.0, cp=750.0, L=230e3, TL=1215.0, TE=1150.0, f_pro=0.3),
    "green_sand": dict(k=0.9, rho=1600.0, cp=1100.0),      # 湿型砂
    "core_sand": dict(k=0.6, rho=1500.0, cp=1050.0),       # 树脂砂芯
    "chill_steel": dict(k=42.0, rho=7800.0, cp=560.0),     # 外冷铁
}
SAND, METAL, CORE, CHILL = 0, 1, 2, 3


@dataclass
class Mold:
    """mat：每格材料号（SAND/METAL/CORE/CHILL）；feeder：哪些金属格是冒口（或浇注系统，补缩源）；dx：格子边长 m"""
    mat: np.ndarray
    dx: float
    feeder: np.ndarray | None = None
    metal: str = "HT250"
    t_pour: float = 1380.0
    t_mold: float = 25.0


# ---------------------------------------------------------------- 体素化
def voxelize(tris: np.ndarray, origin, dx: float, shape) -> np.ndarray:
    """三角网格（n×3×3，单位与 origin、dx 一致，必须封闭）→ 布尔体素（格子中心在里面为 True）。
    做法：沿 x 方向对每一条 (y, z) 射线求与三角形的交点，按奇偶填充。射线位置偏一点点，避开刚好打在棱上。"""
    nx, ny, nz = shape
    ox, oy, oz = origin
    eps = dx * 1e-3
    ys = oy + (np.arange(ny) + 0.5) * dx + eps * 0.37
    zs = oz + (np.arange(nz) + 0.5) * dx + eps * 0.61
    hits = [[] for _ in range(ny * nz)]
    A, B, C = tris[:, 0], tris[:, 1], tris[:, 2]
    for a, b, c in zip(A, B, C):
        ymin, ymax = min(a[1], b[1], c[1]), max(a[1], b[1], c[1])
        zmin, zmax = min(a[2], b[2], c[2]), max(a[2], b[2], c[2])
        j0, j1 = np.searchsorted(ys, ymin), np.searchsorted(ys, ymax)
        k0, k1 = np.searchsorted(zs, zmin), np.searchsorted(zs, zmax)
        if j0 >= j1 or k0 >= k1:
            continue
        Y, Z = np.meshgrid(ys[j0:j1], zs[k0:k1], indexing="ij")
        # 投影到 yz 平面的重心坐标
        d = (b[1] - a[1]) * (c[2] - a[2]) - (c[1] - a[1]) * (b[2] - a[2])
        if abs(d) < 1e-18:
            continue
        l1 = ((Y - a[1]) * (c[2] - a[2]) - (c[1] - a[1]) * (Z - a[2])) / d
        l2 = ((b[1] - a[1]) * (Z - a[2]) - (Y - a[1]) * (b[2] - a[2])) / d
        inside = (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)
        if not inside.any():
            continue
        X = a[0] + l1 * (b[0] - a[0]) + l2 * (c[0] - a[0])
        jj, kk = np.nonzero(inside)
        for j, k, x in zip(jj + j0, kk + k0, X[inside]):
            hits[j * nz + k].append(x)
    xs = ox + (np.arange(nx) + 0.5) * dx
    vox = np.zeros(shape, bool)
    for r, h in enumerate(hits):
        if len(h) < 2:
            continue
        h = np.sort(np.asarray(h))
        if len(h) % 2:
            h = h[:-1]                       # 奇数个交点（擦边）：去掉最后一个，宁可少填
        j, k = divmod(r, nz)
        for x0, x1 in zip(h[0::2], h[1::2]):
            vox[(xs > x0) & (xs < x1), j, k] = True
    return vox


def read_stl(path) -> np.ndarray:
    """二进制或文本 STL → n×3×3"""
    import trimesh
    m = trimesh.load(path, force="mesh")
    return np.asarray(m.vertices)[np.asarray(m.faces)]


# ---------------------------------------------------------------- 焓与温度
class _Enthalpy:
    """单位体积焓 H(T)（J/m³）与反函数，金属分段线性；非金属 H = ρ·cp·T"""

    def __init__(self, m):
        self.m = m
        rc = m["rho"] * m["cp"]
        TL, TE, L, fp = m["TL"], m["TE"], m["L"] * m["rho"], m["f_pro"]
        Ta, Tb = TE + 5.0, TE - 5.0
        self.T = np.array([-100.0, Tb, Ta, TL, 2000.0])
        self.H = np.array([rc * -100.0, rc * Tb, rc * Ta + (1 - fp) * L, rc * TL + L, rc * 2000.0 + L])
        # 固相分数：TL → Ta 线性长到 f_pro（初生奥氏体），Ta → Tb 线性到 1（共晶），Tb 以下全固
        self.fs = np.array([1.0, 1.0, fp, 0.0, 0.0])

    def h(self, T):
        return np.interp(T, self.T, self.H)

    def t(self, H):
        return np.interp(H, self.H, self.T)

    def f_s(self, T):
        return np.interp(T, self.T, self.fs)


# ---------------------------------------------------------------- 求解
def solidify(mold: Mold, t_end=None, fs_crit=0.7, snap_every=5.0, dt=None, progress=None):
    """返回 dict：
    t_sol（每格凝固完 fs ≥ 0.999 的时间，非金属格为 nan）、t_crit（fs 到 fs_crit 的时间）、
    pockets（孤立液相区：体积 cm³、开始孤立的时间、凝固完的时间、中心、包围盒，按体积排序）、
    snaps（每 snap_every 秒金属格的 fs，float16，顺序同 mat == METAL，给出图和动画用）、steps、dt。"""
    mat = mold.mat
    dx = mold.dx
    props = {SAND: MATERIALS["green_sand"], CORE: MATERIALS["core_sand"], CHILL: MATERIALS["chill_steel"], METAL: MATERIALS[mold.metal]}
    k = np.zeros(mat.shape, np.float32)
    rc = np.zeros(mat.shape, np.float32)
    for mid, p in props.items():
        sel = mat == mid
        k[sel] = p["k"]
        rc[sel] = p["rho"] * p["cp"]
    met = mat == METAL
    mi = np.flatnonzero(met)
    inv_rc = (1.0 / rc).astype(np.float32)
    E = _Enthalpy(props[METAL])
    alpha_max = float(np.max(k / rc))
    if dt is None:
        dt = 0.9 * dx * dx / (6 * alpha_max)
    # 面导热（调和平均）× dt / dx²，分三个方向
    def kf(a, b):
        return (2 * a * b / np.maximum(a + b, 1e-12)).astype(np.float32)
    kx, ky, kz = kf(k[1:], k[:-1]), kf(k[:, 1:], k[:, :-1]), kf(k[:, :, 1:], k[:, :, :-1])
    c = np.float32(dt / (dx * dx))
    T = np.where(met, mold.t_pour, mold.t_mold).astype(np.float32)
    H = np.where(met, E.h(T), rc * T).astype(np.float64)
    t_sol = np.full(mat.shape, np.nan, np.float32)
    t_crit = np.full(mat.shape, np.nan, np.float32)
    feeder = mold.feeder if mold.feeder is not None else np.zeros(mat.shape, bool)
    pockets, open_p = [], {}
    snaps = []
    t = 0.0
    step = 0
    next_snap = 0.0
    nmet = int(met.sum())
    while True:
        # 热流
        q = np.zeros(mat.shape, np.float32)
        f = kx * (T[1:] - T[:-1]); q[:-1] += f; q[1:] -= f
        f = ky * (T[:, 1:] - T[:, :-1]); q[:, :-1] += f; q[:, 1:] -= f
        f = kz * (T[:, :, 1:] - T[:, :, :-1]); q[:, :, :-1] += f; q[:, :, 1:] -= f
        H += c * q
        T = (H * inv_rc).astype(np.float32)                 # 非金属格 T = H / ρc
        T.ravel()[mi] = E.t(H.ravel()[mi])                 # 金属格按焓反算（只算金属格，省时间）
        t += dt
        step += 1
        if t >= next_snap or (t_end and t >= t_end):
            fs = np.where(met, E.f_s(T), 1.0)
            newly = met & np.isnan(t_sol) & (fs >= 0.999)
            t_sol[newly] = t
            newc = met & np.isnan(t_crit) & (fs >= fs_crit)
            t_crit[newc] = t
            # 孤立液相：还没到 fs_crit 的金属格按 6 连通分组，不碰冒口（浇注系统）的就是孤立区。
            # 每个孤立区记一个“代表格”（区内固相分数最低、最后凝固的那一格），下一次用代表格认出还是不是同一个区
            liq = met & (fs < fs_crit)
            lab, n = ndimage.label(liq)
            labf = lab.ravel()
            fed = set(np.unique(lab[feeder & liq]).tolist()) if n else set()
            seen = set()
            for key in list(open_p):                       # 已有的孤立区：代表格还在液相里就更新，否则收尾
                p = open_p[key]
                li = int(labf[p["rep"]])
                if li == 0 or li in seen:
                    p["t_end"] = t
                    pockets.append(open_p.pop(key))
                    continue
                seen.add(li)
                p["cells_now"] = int((labf == li).sum())
            if n:
                objs = ndimage.find_objects(lab)
                for li in range(1, n + 1):
                    if li in fed or li in seen or objs[li - 1] is None:
                        continue
                    sl = objs[li - 1]
                    sub = lab[sl] == li
                    cells = int(sub.sum())
                    fsub = np.where(sub, fs[sl], 2.0)
                    loc = np.unravel_index(int(np.argmin(fsub)), fsub.shape)
                    g = tuple(s.start + l_ for s, l_ in zip(sl, loc))
                    rep = int(np.ravel_multi_index(g, mat.shape))
                    open_p[rep] = dict(rep=rep, box=tuple((s.start, s.stop) for s in sl), t_iso=t, cells=cells,
                                       center=tuple(int(v) for v in g))
            snaps.append((round(t, 2), fs[met].astype(np.float16)))      # 只存金属格（省内存），顺序同 mat == METAL
            next_snap += snap_every
            if progress:
                progress(t, float(np.isnan(t_sol[met]).sum()) / max(nmet, 1))
            if not np.isnan(t_sol[met]).any():
                break
            if t_end and t >= t_end:
                break
    for p in open_p.values():
        p["t_end"] = None
        pockets.append(p)
    vc = (dx * 100) ** 3                                     # 一格的体积 cm³
    for p in pockets:
        p["volume_cm3"] = round(p["cells"] * vc, 2)
    pockets.sort(key=lambda p: -p["cells"])
    return dict(t_sol=t_sol, t_crit=t_crit, pockets=pockets, snaps=snaps, steps=step, dt=dt, t_total=t)


# ---------------------------------------------------------------- 标定：平板的 Chvorinov 常数
def plate_test(thick_mm=20.0, dx_mm=2.0, sand_mm=60.0, metal="HT250"):
    """无限大平板（两面贴砂）凝固时间；返回 (t_s, 模数 cm, B = t / M² s/cm²)。用来把凝固时间换成热模数。"""
    n_m = int(round(thick_mm / dx_mm))
    n_s = int(round(sand_mm / dx_mm))
    n = n_m + 2 * n_s
    mat = np.full((n, 3, 3), SAND, np.int8)
    mat[n_s:n_s + n_m] = METAL
    r = solidify(Mold(mat=mat, dx=dx_mm / 1000, metal=metal), snap_every=0.5)
    ts = float(np.nanmax(r["t_sol"]))
    M = thick_mm / 2 / 10                                    # 平板模数 = 厚度 / 2（cm）
    return ts, M, ts / (M * M)


def modulus(t_sol, B):
    """凝固时间（s）→ 热模数（cm），M = √(t / B)"""
    return np.sqrt(np.maximum(t_sol, 0) / B)
