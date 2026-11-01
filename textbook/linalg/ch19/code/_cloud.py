"""本章共用：深度相机拍到的一幅点云（模拟数据）。以下划线开头，构建时不单独运行。

场景（单位 m）：桌面 z = 0；一个箱盖毛坯（长方体，x ∈ [−0.12, 0]，y ∈ [−0.06, 0.04]，高 0.05）；
一段竖放的轴（圆柱，中心 (0.08, 0)，半径 0.03，高 0.07）。相机在 C = (0, −0.45, 0.55)。
各表面按 4 mm 的网格取点，只保留朝向相机、且从相机看不被箱子和圆柱挡住的点；
每个点沿视线方向加 1 mm 的随机误差（深度相机的误差主要在深度方向）。同时记下每个点的真实法向和到棱边的距离。
"""
import math

import numpy as np

CAM = np.array([0.0, -0.45, 0.55])
BOX = (np.array([-0.12, -0.06, 0.0]), np.array([0.0, 0.04, 0.05]))
CYL_C, CYL_R, CYL_H = np.array([0.08, 0.0]), 0.03, 0.07
STEP, NOISE = 0.004, 0.001


def _hit_box(P, D):
    """从 P 沿 D（到相机）的线段是否穿过长方体（不含端点附近）。"""
    lo, hi = BOX
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = (lo - P) / D
        t2 = (hi - P) / D
    tmin = np.nanmax(np.minimum(t1, t2), axis=1)
    tmax = np.nanmin(np.maximum(t1, t2), axis=1)
    return (tmax > np.maximum(tmin, 1e-6)) & (tmin < 1.0)


def _hit_cyl(P, D):
    q = P[:, :2] - CYL_C
    d = D[:, :2]
    a = np.sum(d * d, axis=1)
    b = 2 * np.sum(q * d, axis=1)
    c = np.sum(q * q, axis=1) - CYL_R ** 2
    disc = b * b - 4 * a * c
    hit = np.zeros(len(P), bool)
    ok = disc > 0
    sq = np.sqrt(np.where(ok, disc, 0))
    for t in ((-b - sq) / (2 * a), (-b + sq) / (2 * a)):
        z = P[:, 2] + t * D[:, 2]
        hit |= ok & (t > 1e-6) & (t < 1.0) & (z > 0) & (z < CYL_H)
    # 顶盖
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (CYL_H - P[:, 2]) / D[:, 2]
    xy = P[:, :2] + t[:, None] * D[:, :2] - CYL_C
    hit |= (t > 1e-6) & (t < 1.0) & (np.sum(xy * xy, axis=1) < CYL_R ** 2)
    return hit


def _grid(a0, a1, b0, b1):
    a = np.arange(a0 + STEP / 2, a1, STEP)
    b = np.arange(b0 + STEP / 2, b1, STEP)
    A, B = np.meshgrid(a, b)
    return A.ravel(), B.ravel()


def scan(seed=2026):
    pts, nrm, edge = [], [], []
    lo, hi = BOX
    # 桌面（去掉箱子、圆柱的底面范围）
    x, y = _grid(-0.2, 0.2, -0.15, 0.15)
    keep = ~((x > lo[0]) & (x < hi[0]) & (y > lo[1]) & (y < hi[1])) & ((x - CYL_C[0]) ** 2 + (y - CYL_C[1]) ** 2 > CYL_R ** 2)
    x, y = x[keep], y[keep]
    P = np.c_[x, y, np.zeros_like(x)]
    dbox = np.hypot(np.maximum.reduce([lo[0] - x, x - hi[0], 0 * x]), np.maximum.reduce([lo[1] - y, y - hi[1], 0 * y]))
    dcyl = np.hypot(x - CYL_C[0], y - CYL_C[1]) - CYL_R
    pts.append(P); nrm.append(np.tile([0, 0, 1.0], (len(x), 1))); edge.append(np.minimum(dbox, dcyl))          # 桌面的外沿不是棱边，只算与箱子、圆柱的交线
    # 箱子顶面
    x, y = _grid(lo[0], hi[0], lo[1], hi[1])
    pts.append(np.c_[x, y, np.full_like(x, hi[2])]); nrm.append(np.tile([0, 0, 1.0], (len(x), 1)))
    edge.append(np.minimum.reduce([x - lo[0], hi[0] - x, y - lo[1], hi[1] - y]))
    # 箱子前面（y = lo[1]，法向 −y）和左面（x = lo[0]，法向 −x）
    x, z = _grid(lo[0], hi[0], 0.0, hi[2])
    pts.append(np.c_[x, np.full_like(x, lo[1]), z]); nrm.append(np.tile([0, -1.0, 0], (len(x), 1)))
    edge.append(np.minimum.reduce([x - lo[0], hi[0] - x, z, hi[2] - z]))
    y, z = _grid(lo[1], hi[1], 0.0, hi[2])
    pts.append(np.c_[np.full_like(y, lo[0]), y, z]); nrm.append(np.tile([-1.0, 0, 0], (len(y), 1)))
    edge.append(np.minimum.reduce([y - lo[1], hi[1] - y, z, hi[2] - z]))
    # 圆柱侧面与顶面
    nth = int(round(2 * math.pi * CYL_R / STEP))
    th = (np.arange(nth) + 0.5) * 2 * math.pi / nth
    z = np.arange(STEP / 2, CYL_H, STEP)
    TH, Zc = np.meshgrid(th, z)
    TH, Zc = TH.ravel(), Zc.ravel()
    pts.append(np.c_[CYL_C[0] + CYL_R * np.cos(TH), CYL_C[1] + CYL_R * np.sin(TH), Zc])
    nrm.append(np.c_[np.cos(TH), np.sin(TH), np.zeros_like(TH)])
    edge.append(np.minimum(Zc, CYL_H - Zc))
    x, y = _grid(CYL_C[0] - CYL_R, CYL_C[0] + CYL_R, CYL_C[1] - CYL_R, CYL_C[1] + CYL_R)
    r = np.hypot(x - CYL_C[0], y - CYL_C[1])
    k = r < CYL_R
    pts.append(np.c_[x[k], y[k], np.full(k.sum(), CYL_H)]); nrm.append(np.tile([0, 0, 1.0], (k.sum(), 1)))
    edge.append(CYL_R - r[k])
    P, Nn, E = np.vstack(pts), np.vstack(nrm), np.concatenate(edge)
    # 只留朝向相机且不被挡住的点
    D = CAM - P
    vis = (np.sum(Nn * D, axis=1) > 0) & ~_hit_box(P + 1e-5 * Nn, D) & ~_hit_cyl(P + 1e-5 * Nn, D)
    P, Nn, E, D = P[vis], Nn[vis], E[vis], D[vis]
    rng = np.random.default_rng(seed)
    ray = D / np.linalg.norm(D, axis=1, keepdims=True)
    P = P + NOISE * rng.standard_normal(len(P))[:, None] * ray
    return P, Nn, E


def normals(P, k):
    """每个点取 k 个最近邻（含自己），局部协方差最小特征值的特征向量为法向；曲面变化度 λ₃/(λ₁ + λ₂ + λ₃)；
    法向朝向相机。"""
    from scipy.spatial import cKDTree
    _, idx = cKDTree(P).query(P, k=k)
    Q = P[idx]                                   # n×k×3
    Q = Q - Q.mean(axis=1, keepdims=True)
    C = np.einsum("nki,nkj->nij", Q, Q) / k
    w, V = np.linalg.eigh(C)                     # 特征值从小到大
    n = V[:, :, 0]
    flip = np.sum(n * (CAM - P), axis=1) < 0
    n[flip] *= -1
    return n, w[:, 0] / w.sum(axis=1), flip
