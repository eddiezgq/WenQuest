"""第 138 轮 G4.6：送布组的尺寸综合与运动（送布、抬牙、针距调节与倒缝）。

    python3 tools/wqls/g4_feed.py [<输出目录>]   → docs/设计/WQ-LS/G4/送布机构.json、送布牙轨迹.png

目标轨迹（不改）：设计软件 sewcore 的送布牙椭圆——
  前后（y，往后为正）：X(φ) = (S/2)·cos(φ − φF)，S = 针距 / 0.926，φF = 108.2°；
  上下（牙齿顶面高出针板）：Y(φ) = (h − A) + A·cos(φ − φL)，h 0.8、A 1.1、φL = 34°（G1 定送布定时提前 6°）。
机构（都在垂直于 x 的平面里，坐标 (y, z)，与整机相同）：
  送布链（x ≈ 331，立柱脚下的机座里）：上轴送布偏心 E → 送布连杆（竖直，长 L1）→ 调节器滑槽上的滑块 P（滑槽过 G，
    α = 0 时滑槽垂直于 L2；α 由针距旋钮、倒缝扳手定，α = 0 不送布，α < 0 倒缝）→ 水平连杆 L2 → 送布摆轴曲柄销 C
    （摆轴中心 Fr，曲柄 rc）→ 摆轴前端摆杆（ra，朝上）的销 T：牙架后铰点。
  抬牙链（x ≈ 113）：下轴抬牙偏心 → 抬牙连杆 L3 → 抬牙摆轴曲柄销 D（摆轴中心 Lr，曲柄 rd）→ 摆轴前端叉子 K（rf）：
    牙架前端的滑块在叉子的槽里，只受上下约束。
  牙架：后铰点 T、前端叉子处的滑块，牙架上离 T 为 d 的地方装送布牙（牙齿顶面比牙架线高 hd）。
尺寸：机座、立柱里的空间定下摆轴中心、摆杆长度等（见 GEO）；偏心量、偏心相位、调节器各档的 α、牙齿高度
由最小二乘按目标轨迹拟合（针距 1–5 mm、倒缝 1–5 mm 同时拟合）。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "factory" / "digital"), str(ROOT / "services" / "gateway"), str(HERE)]
from app.sewcore.kit import Mech  # noqa: E402
from cae import linkage as L  # noqa: E402
import spec as S  # noqa: E402

DEG = math.pi / 180
N = 180                                   # 一转 2° 一点
PHI = np.arange(N) * 2.0
STITCH = (1.0, 2.0, 3.0, 4.0, 5.0)

# 空间定下来的几何（mm）：(y, z)
GEO = dict(
    O1=(0.0, S.ZU),                 # 上轴
    O2=(S.YL, S.ZL),                # 下轴
    G=(60.0, -22.0),                # 调节器滑槽中心（滑块 P 的平均位置），机座里、立柱脚下
    Fr=(-18.0, -32.0), rc=12.0,     # 送布摆轴中心、曲柄（朝上）
    ra=24.0,                        # 送布摆轴前端摆杆（朝上）→ 牙架后铰点 T
    Lr=(55.0, -20.0), rd=12.0,      # 抬牙摆轴中心、曲柄
    rf=27.3,                        # 抬牙叉子臂长（从 Lr 指向 (30, −9) 附近）
    yk=30.0,                        # 叉子在牙架上的位置（牙架前端滑块的 y）
    d=18.0,                         # 送布牙中心离 T 的距离（牙在针的位置 y = 0）
)


def target(s, rev=False):
    m = Mech()
    F = m.feed_model(s=s, dT=S.SEW["dT"], h=S.SEW["h"])
    X = np.array([F["X"](p) for p in PHI])
    Y = np.array([F["Y"](p) for p in PHI])
    return (-X if rev else X), Y, F


def mean_C():
    """送布摆轴曲柄销的平均位置：曲柄朝上"""
    Fr, rc = GEO["Fr"], GEO["rc"]
    return (Fr[0], Fr[1] + rc)


def mean_D():
    Lr, rd = GEO["Lr"], GEO["rd"]
    # 抬牙曲柄朝前下方，垂直于抬牙连杆（连杆从下轴指过来）
    O2 = GEO["O2"]
    u = np.array(Lr) - np.array(O2)
    u /= np.linalg.norm(u)
    n = np.array([-u[1], u[0]])
    return tuple(np.array(Lr) - rd * n)


def kin(p, alpha, full=False):
    """一转的送布牙位置。p：拟合参数 dict；alpha：调节器角（rad）"""
    O1, O2, G = GEO["O1"], GEO["O2"], GEO["G"]
    Fr, rc, ra = GEO["Fr"], GEO["rc"], GEO["ra"]
    Lr, rd, rf = GEO["Lr"], GEO["rd"], GEO["rf"]
    C0, D0 = mean_C(), mean_D()
    # α = 0 时滑槽垂直于水平连杆 L2（滑块沿槽动时，L2 只有二阶的动作 → 不送布）
    a0 = math.atan2(C0[1] - G[1], C0[0] - G[0]) - math.pi / 2
    u = (math.cos(a0 + alpha), math.sin(a0 + alpha))
    L1 = math.dist(O1, G)
    L2 = math.dist(G, C0)
    L3 = math.dist(O2, D0)
    beta0 = L.angle(Fr, C0)
    T0 = (Fr[0], Fr[1] + ra)
    gam0 = L.angle(Lr, D0)
    K0 = (GEO["yk"], T0[1] + p["dzk"])                  # 叉子平均位置（与牙架同高附近）
    rfa = math.dist(Lr, K0)
    out = dict(y=[], z=[], P=[], C=[], T=[], D=[], K=[], E=[], EL=[])
    nearP, nearC, nearD = G, C0, D0
    for ph in PHI:
        t = ph * DEG
        E = L.crank(O1, p["eF"], t + p["thF"])
        P, _s = L.rrp(E, L1, G, u, nearP)
        C = L.rrr(P, L2, Fr, rc, nearC)
        beta = L.angle(Fr, C) - beta0
        T = L.rotate_about(T0, Fr, beta)
        EL = L.crank(O2, p["eL"], t + p["thL"])
        D = L.rrr(EL, L3, Lr, rd, nearD)
        gam = L.angle(Lr, D) - gam0
        K = L.rotate_about(K0, Lr, gam)
        # 牙架：过 T，前端滑块在叉子里只受上下约束 → 牙架方向由 T 和 K 的高度定（K 的 y 只让滑块在槽里滑）
        dy, dz = K[0] - T[0], K[1] - T[1]
        psi = math.atan2(dz, dy)
        dog_y = T[0] + GEO["d"] * math.cos(psi) - p["hd"] * math.sin(psi)
        dog_z = T[1] + GEO["d"] * math.sin(psi) + p["hd"] * math.cos(psi)
        out["y"].append(dog_y)
        out["z"].append(dog_z)
        if full:
            for k_, v_ in (("P", P), ("C", C), ("T", T), ("D", D), ("K", K), ("E", E), ("EL", EL)):
                out[k_].append(v_)
        nearP, nearC, nearD = P, C, D
    out["y"], out["z"] = np.array(out["y"]), np.array(out["z"])
    out.update(L1=L1, L2=L2, L3=L3, rfa=rfa)
    return out


PNAMES = ["eF", "thF", "eL", "thL", "hd", "dzk"]


def unpack(x):
    p = dict(zip(PNAMES, x[:len(PNAMES)]))
    al = x[len(PNAMES):]
    return p, al


def residual(x):
    p, al = unpack(x)
    r = []
    for i, s in enumerate(STITCH):
        for rev, a in ((False, al[i]), (True, -al[len(STITCH) + i])):
            X, Y, _ = target(s, rev)
            try:
                k = kin(p, a)
            except ValueError:
                return np.full(len(STITCH) * 2 * N * 2 + len(STITCH) * 2, 50.0)
            ym = k["y"] - np.mean(k["y"])
            r += list(ym - X) + list(k["z"] - Y)
    # 牙在针板槽里的平均位置不随针距漂移太多（≤ 0.5 mm 算合格，这里轻罚）
    for i, s in enumerate(STITCH):
        for a in (al[i], -al[len(STITCH) + i]):
            r.append(0.2 * (np.mean(kin(p, a)["y"]) - 0.0))
    return np.array(r)


_TC = {}


def target(s, rev=False):  # noqa: F811  （带缓存）
    key = (s, rev)
    if key not in _TC:
        m = Mech()
        F = m.feed_model(s=s, dT=S.SEW["dT"], h=S.SEW["h"])
        X = np.array([F["X"](p) for p in PHI])
        Y = np.array([F["Y"](p) for p in PHI])
        _TC[key] = ((-X if rev else X), Y, F)
    return _TC[key]


def synth():
    x0 = [2.5, 0.0, 1.3, 0.0, 6.0, 0.0] + [0.05 * s for s in STITCH] * 2
    best = None
    for thF0 in np.radians(np.arange(0, 360, 90)):
        for thL0 in np.radians(np.arange(0, 360, 90)):
            x = list(x0)
            x[1], x[3] = thF0, thL0
            try:
                r = least_squares(residual, x, method="lm", max_nfev=120)
            except Exception:  # noqa: BLE001
                continue
            if best is None or r.cost < best.cost:
                best = r
    r = least_squares(residual, best.x, method="lm", max_nfev=4000)
    return r


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "设计" / "WQ-LS" / "G4"
    r = synth()
    p, al = unpack(r.x)
    res = dict(geo={k: (list(v) if isinstance(v, tuple) else v) for k, v in GEO.items()}, params={k: float(v) for k, v in p.items()},
               settings=[])
    worst = 0.0
    for i, s in enumerate(STITCH):
        for rev, a in ((False, al[i]), (True, -al[len(STITCH) + i])):
            X, Y, F = target(s, rev)
            k = kin(p, a)
            ym = k["y"] - np.mean(k["y"])
            ey, ez = np.max(np.abs(ym - X)), np.max(np.abs(k["z"] - Y))
            stitch = abs(ym.max() - ym.min()) * 0.926
            worst = max(worst, ey, ez)
            res["settings"].append(dict(s=s, reverse=rev, alpha_deg=round(math.degrees(a), 3), err_y=round(float(ey), 4), err_z=round(float(ez), 4),
                                        y_mean=round(float(np.mean(k["y"])), 3), stitch_est=round(float(stitch), 3)))
    res["worst_mm"] = round(float(worst), 4)
    print(json.dumps(res, ensure_ascii=False, indent=1)[:3000])


if __name__ == "__main__":
    main()
