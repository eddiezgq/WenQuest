"""第 138 轮 G4.6：送布组的尺寸综合与运动（送布、抬牙、针距调节与倒缝）。

    python3 tools/wqls/g4_feed.py [<输出目录>]   → docs/设计/WQ-LS/G4/送布机构.json、送布牙轨迹.png

目标轨迹（不改）：设计软件 sewcore 的送布牙椭圆——
  前后（y，往后为正）：X(φ) = (S/2)·cos(φ − φF)，S = 针距 / 0.926，φF = 108.2°；
  上下（牙齿顶面高出针板）：Y(φ) = (h − A) + A·cos(φ − φL)，h 0.8、A 1.1、φL = 34°（G1 定送布定时提前 6°）。
机构（都在垂直于 x 的平面里，坐标 (y, z)，与整机相同）：
  送布链（x ≈ 331，立柱脚下的机座里）：上轴送布偏心 E → 送布连杆（竖直，长 L1，在上轴正下方）→ 调节器滑槽上的滑块 P（滑槽过 G，
    α = 0 时滑槽垂直于 L2；α 由针距旋钮、倒缝扳手定，α = 0 不送布，α < 0 倒缝）→ 水平连杆 L2 → 送布摆轴曲柄销 C
    （摆轴中心 Fr，曲柄 rc）→ 摆轴前端摆杆（ra，朝上）的销 T：牙架后铰点。
  抬牙链（x ≈ 113）：下轴抬牙偏心 → 抬牙连杆 L3 → 抬牙摆轴曲柄销 D（摆轴中心 Lr，曲柄 rd）→ 摆轴前端叉子 K：
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
    G=(0.0, -50.0),                 # 调节器滑槽中心（滑块 P 的平均位置）：上轴正下方（送布连杆竖直），机座里、立柱脚下、下轴下面
    Fr=(76.0, -40.0), rc=10.0,      # 送布摆轴（机座后部）中心、曲柄（朝下，曲柄销与 G 同高 → L2 水平，正倒缝对称）；
                                    #   y 76 让开立柱脚的螺钉凸台；L2 在下轴、下带轮轮毂下面 2.6 mm 过去
    ra=27.0,                        # 送布摆轴前端摆杆（朝上）→ 牙架后铰点 T (76, −13)：牙架顶在机座顶板下 3 mm 以上
    Lr=(-45.0, -28.0), rd=12.0,     # 抬牙摆轴（机座前部）中心、曲柄
    yk=-30.0,                       # 叉子在牙架前端滑块处的 y
    d=78.0,                         # 送布牙中心离 T 的距离（牙在针的位置 y = 0）
)


def target(s, rev=False):
    m = Mech()
    F = m.feed_model(s=s, dT=S.SEW["dT"], h=S.SEW["h"])
    X = np.array([F["X"](p) for p in PHI])
    Y = np.array([F["Y"](p) for p in PHI])
    return (-X if rev else X), Y, F


def mean_C():
    """送布摆轴曲柄销的平均位置：曲柄朝下"""
    Fr, rc = GEO["Fr"], GEO["rc"]
    return (Fr[0], Fr[1] - rc)


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
    Lr, rd = GEO["Lr"], GEO["rd"]
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
        by, bz = math.cos(psi), math.sin(psi)              # 牙架方向（从 T 指向叉子）
        ny, nz = (-bz, by) if by > 0 else (bz, -by)       # 牙架的“上”法向
        dog_y = T[0] + GEO["d"] * by + p["hd"] * ny
        dog_z = T[1] + GEO["d"] * bz + p["hd"] * nz
        out["y"].append(dog_y)
        out["z"].append(dog_z)
        if full:
            for k_, v_ in (("P", P), ("C", C), ("T", T), ("D", D), ("K", K), ("E", E), ("EL", EL)):
                out[k_].append(v_)
            out.setdefault("dog", []).append((dog_y, dog_z))
            out.setdefault("beta", []).append(beta)
            out.setdefault("gam", []).append(gam)
        nearP, nearC, nearD = P, C, D
    out["y"], out["z"] = np.array(out["y"]), np.array(out["z"])
    out.update(L1=L1, L2=L2, L3=L3, rfa=rfa, T0=T0, K0=K0, C0=C0, D0=D0, u=u)
    return out


PNAMES = ["thF", "eL", "thL", "hd", "dzk"]
E_F = 3.0                                 # 送布偏心量（定值；针距由调节器角 α 定）
LB = [-20, 0.3, -20, 2.0, -3.0]
UB = [20, 5.0, 20, 12.0, 3.0]


def unpack(x):
    p = dict(zip(PNAMES, x[:len(PNAMES)]))
    p["eF"] = E_F
    al = x[len(PNAMES):]
    return p, al


def residual(x):
    p, al = unpack(x)
    r = []
    for i, s in enumerate(STITCH):
        for rev, a in ((False, al[i]), (True, al[len(STITCH) + i])):
            X, Y, _ = target(s, rev)
            try:
                k = kin(p, a)
            except ValueError:
                return np.full(len(STITCH) * 2 * (N * 2 + 1), 50.0)
            ym = k["y"] - np.mean(k["y"])
            r += list(ym - X) + list(k["z"] - Y) + [0.2 * np.mean(k["y"])]   # 牙的平均位置不随针距漂移（轻罚）
            if PENALTY:                                  # 第二步：sewcore 判据——拖布留 30% 余量、牙顶高度 0.8
                c = feed_check(k, s, rev)
                if "drag" in c:
                    r += [20 * max(0.0, c["drag"] - 0.035), 3 * (c["top"] - S.SEW["h"])]
                else:
                    r += [5.0, 5.0]
    return np.array(r)


_TC = {}
PENALTY = False
FAB = "cotton"


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
    """先只拟合抬牙（α = 0），再只拟合送布相位和 5 mm 的 α，最后全部一起拟合"""
    X5, Y5, _ = target(5.0)
    best = None
    for t in np.radians(range(0, 360, 30)):
        def rz(x):
            p = dict(eF=E_F, thF=0.0, eL=x[0], thL=x[1], hd=x[2], dzk=x[3])
            return kin(p, 0.0)["z"] - Y5
        r = least_squares(rz, [1.3, t, 7.0, 0.0], bounds=([0.3, -20, 2, -3], [5, 20, 12, 3]))
        if best is None or r.cost < best.cost:
            best = r
    eL, thL, hd, dzk = best.x
    best2 = None
    for t in np.radians(range(0, 360, 30)):
        def ry(x):
            k = kin(dict(eF=E_F, thF=x[0], eL=eL, thL=thL, hd=hd, dzk=dzk), x[1])
            return k["y"] - k["y"].mean() - X5
        try:
            r = least_squares(ry, [t, 0.4], bounds=([-20, -1.4], [20, 1.4]))
        except ValueError:
            continue
        if best2 is None or r.cost < best2.cost:
            best2 = r
    thF, a5 = best2.x
    al0 = [a5 * s / 5 for s in STITCH] + [-a5 * s / 5 for s in STITCH]
    x0 = [thF, eL, thL, hd, dzk] + al0
    lb = LB + [-1.4] * len(al0)
    ub = UB + [1.4] * len(al0)
    r = least_squares(residual, x0, bounds=(lb, ub), max_nfev=3000)
    return refine(r.x)


def criteria_cost(xp, al_guess, out=None):
    """sewcore 判据的目标函数：拖布留余量（≤ 0.04）、牙顶 0.8、针距用 α 二分法对准，再加一点椭圆偏差"""
    p = dict(zip(PNAMES, xp))
    p["eF"] = E_F
    cost, als = 0.0, []
    try:
        for i, s in enumerate(STITCH):
            for j, rev in enumerate((False, True)):
                a = alpha_for(p, s, rev, al_guess[i + j * len(STITCH)])
                k = kin(p, a)
                c = feed_check(k, s, rev)
                if "drag" not in c:
                    return 1e3
                X, Y, _ = target(s, rev)
                dev = np.mean((k["y"] - k["y"].mean() - X) ** 2 + (k["z"] - Y) ** 2)
                cost += 200 * max(0.0, c["drag"] - 0.04) ** 2 + 20 * (c["top"] - S.SEW["h"]) ** 2 + 0.01 * dev + 50 * c["stitch_err"] ** 2
                cost += 2 * max(0.0, 25 - c["feedrise"]) ** 2 / 100
                als.append(a)
    except ValueError:
        return 1e3
    if out is not None:
        out[:] = als
    return cost


def refine(x):
    """最小二乘拟合椭圆之后，按判据用单纯形法再调相位、抬牙偏心、牙齿高度"""
    from scipy.optimize import minimize
    xp, al = list(x[:len(PNAMES)]), list(x[len(PNAMES):])
    r = minimize(lambda v: criteria_cost(v, al), xp, method="Nelder-Mead", options=dict(maxiter=600, xatol=1e-4, fatol=1e-7))
    als = []
    criteria_cost(r.x, al, als)
    class R:  # noqa: N801
        pass
    R.x = np.r_[r.x, als]
    return R




def feed_check(k, s_nom, rev=False):
    """按 sewcore 的送布判据校核机构的实际轨迹（同 kit.feed_model 的算法，只是轨迹换成机构算出来的）：
    牙齿顶面高出针板（z > 0）的区间是送布区间；拖布 = 针在布里（ain < φ < 360 − ain）时牙还在动的水平距离；
    实际针距 = 送布区间里牙走的水平距离；起牙定时 = 起牙角离针出布的角度（20…180°）。"""
    from app.sewcore.kit import FEED_FAB
    m = Mech()
    t = FEED_FAB[FAB]["t"]
    ain = m.cross(t)
    y, z = k["y"], k["z"]
    up = z > 0
    i_r = [i for i in range(N) if up[i] and not up[i - 1]]
    i_d = [i for i in range(N) if not up[i] and up[i - 1]]
    if len(i_r) != 1 or len(i_d) != 1:
        return dict(ok=False, why="牙一转里出针板的次数不是一次")

    def cross_ang(i):                          # 线性插值求 z = 0 的角度
        z0, z1 = z[i - 1], z[i]
        return (PHI[i - 1] + 2.0 * (0 - z0) / (z1 - z0)) % 360
    rise, drop = cross_ang(i_r[0]), cross_ang(i_d[0])
    # 细分一转（插值）算拖布和实际针距
    ph = np.arange(0, 360, 0.25)
    yi = np.interp(ph, np.r_[PHI, 360], np.r_[y, y[0]])
    zi = np.interp(ph, np.r_[PHI, 360], np.r_[z, z[0]])
    dy = np.diff(np.r_[yi, yi[0]])
    on = zi > 0
    pm = (ph + 0.125) % 360
    infab = (pm > ain) & (pm < 360 - ain)
    drag = float(np.sum(np.abs(dy[on & infab])))
    net = float(np.sum(dy[on]))
    fr = (rise - (360 - ain) + 360) % 360
    sgn = -1 if rev else 1
    err = (net * sgn - s_nom) / s_nom
    return dict(rise=round(float(rise), 1), drop=round(float(drop), 1), drag=round(drag, 4), net=round(net, 3), top=round(float(z.max()), 3),
                feedrise=round(float(fr), 1), stitch_err=round(float(err), 4),
                ok=bool(drag <= 0.05 and 20 <= fr < 180 and abs(err) <= 0.05))


def alpha_for(p, s_nom, rev, a_guess):
    """调节器角：二分法使实际针距 = 名义针距"""
    from scipy.optimize import brentq
    sgn = -1 if rev else 1
    f = lambda a: feed_check(kin(p, a), s_nom, rev)["net"] * sgn - s_nom      # noqa: E731
    b = min(1.0, 2 * abs(a_guess) + 0.1)
    lo, hi = (0.0, b) if not rev else (-b, 0.0)
    try:
        return brentq(f, lo, hi, xtol=1e-6) if f(lo) * f(hi) < 0 else a_guess
    except ValueError:
        return a_guess


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "设计" / "WQ-LS" / "G4"
    r = synth()
    p, al = unpack(r.x)
    res = dict(geo={k: (list(v) if isinstance(v, tuple) else v) for k, v in GEO.items()}, params={k: float(v) for k, v in p.items()},
               settings=[])
    worst = 0.0
    for i, s in enumerate(STITCH):
        for rev, a0 in ((False, al[i]), (True, al[len(STITCH) + i])):
            a = alpha_for(p, s, rev, a0)
            X, Y, F = target(s, rev)
            k = kin(p, a)
            ym = k["y"] - np.mean(k["y"])
            ey, ez = np.max(np.abs(ym - X)), np.max(np.abs(k["z"] - Y))
            worst = max(worst, ey, ez)
            res["settings"].append(dict(s=s, reverse=rev, alpha_deg=round(math.degrees(a), 3), dev_y=round(float(ey), 3), dev_z=round(float(ez), 3),
                                        y_mean=round(float(np.mean(k["y"])), 3), check=feed_check(k, s, rev)))
    # 倒缝扳手：把调节器从 +α 扳到 −α（对称），倒缝针距与正缝之比
    # 调节器的零位：正、倒缝调节器角的中点（不送布的那个角），做进零件里；倒缝扳手绕零位对称地扳过去
    mirror = []
    fw = {x["s"]: x["alpha_deg"] for x in res["settings"] if not x["reverse"]}
    bw = {x["s"]: x["alpha_deg"] for x in res["settings"] if x["reverse"]}
    a0 = float(np.mean([(fw[s_] + bw[s_]) / 2 for s_ in fw]))
    res["alpha_zero_deg"] = round(a0, 3)
    for s_, a_ in fw.items():
        c = feed_check(kin(p, math.radians(2 * a0 - a_)), s_, True)
        mirror.append(dict(s=float(s_), reverse_stitch=round(-c["net"], 3), ratio=round(-c["net"] / s_, 4)))
    res["reverse_by_mirror"] = mirror
    # 针距旋钮：α 与针距的线性拟合，按直线刻度时的针距误差
    ss = np.array(list(fw.keys()))
    aa = np.array(list(fw.values()))
    k_, b_ = np.polyfit(ss, aa, 1)
    lin = []
    for s_, a_ in zip(ss, aa):
        c = feed_check(kin(p, math.radians(k_ * s_ + b_)), s_)
        lin.append(round(c["net"] - s_, 3))
    res["dial"] = dict(alpha_per_mm_deg=round(float(k_), 3), alpha0_deg=round(float(b_), 3), stitch_err_linear_mm=[float(v) for v in lin])
    # 给三维和干涉检查用的位置（每 2°）：3 mm 正缝（动画）、5 mm 正缝和倒缝（干涉检查的两个极端）
    poses = {}
    for key, s_, rev in (("s3", 3.0, False), ("s5", 5.0, False), ("r5", 5.0, True)):
        a = next(math.radians(x["alpha_deg"]) for x in res["settings"] if x["s"] == s_ and x["reverse"] == rev)
        k = kin(p, a, full=True)
        rnd = lambda v: [round(float(c), 4) for c in v]                   # noqa: E731
        poses[key] = dict(alpha=round(a, 6), u=rnd(k["u"]), T0=rnd(k["T0"]), K0=rnd(k["K0"]), C0=rnd(k["C0"]), D0=rnd(k["D0"]),
                          L1=round(k["L1"], 4), L2=round(k["L2"], 4), L3=round(k["L3"], 4),
                          **{n: [rnd(v) for v in k[n]] for n in ("E", "P", "C", "T", "D", "K", "EL", "dog")},
                          beta=[round(float(v), 6) for v in k["beta"]], gam=[round(float(v), 6) for v in k["gam"]])
    res["poses"] = poses
    res["dev_worst_mm"] = round(float(worst), 3)
    res["all_ok"] = bool(all(x["check"]["ok"] for x in res["settings"]) and all(abs(m["ratio"] - 1) <= 0.05 for m in mirror)
                     and max(abs(v) for v in lin) <= 0.2)
    (out / "送布机构.json").write_text(json.dumps(res, ensure_ascii=False))
    for x in res["settings"]:
        print(x["s"], "倒" if x["reverse"] else "正", x["alpha_deg"], x["dev_y"], x["dev_z"], x["check"])
    print("倒缝（对称）", mirror)
    print("旋钮", res["dial"])
    print("params", res["params"], "all_ok", res["all_ok"])


if __name__ == "__main__":
    main()
