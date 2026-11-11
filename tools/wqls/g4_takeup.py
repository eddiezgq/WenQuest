"""第 138 轮 G4：挑线机构改为“挑线杆与针杆连杆共用曲柄销”，重新综合四连杆。

为什么改：教材（设计软件）的挑线曲柄在刺布曲柄对面、半径 20.7，单独一根销。做实体时发现两根销装不下——
  挑线杆一转里要扫过上轴中心（离轴心最近 0.2 mm），只能装在轴端外侧；这样刺布曲柄销要穿过挑线杆的平面，
  挑线销要穿过连杆的平面，两处都撞（最近 0.15 mm、0.27 mm）。真机（Juki DDL 等）的做法是挑线杆和连杆套在同一根曲柄销上。
做法：曲柄半径 = 刺布曲柄 15.5，相位与刺布曲柄相同（设计软件里 d = 180°）。用设计软件的 Mech.takeup 算供线、耗线和判据，
  在 a、b、c、线眼偏角、摇杆支点 Q、两个导线点里搜索（差分进化 + Nelder–Mead，种子固定，见 search()）：
  判据照设计软件（余量 ≥ 1 mm、入布前不缺线 ≤ 1 mm、入布前多余 ≤ 行程），再加实体约束：
  - 线眼一转里伸出机头前壁（y = -48）至少 10 mm、最多 37 mm，余量 1–6 mm（太多钩线时线松在旋梭周围），
    线眼最高点不低于上轴中心（穿线时挑线杆在最高处，同类工业平缝机都在这个高度），上下在前盖板能开的竖槽里（z 126–228）；
  - 摇杆装在挑线杆内侧（与曲柄、平衡块外径 34 同一平面，摇杆一转里离轴心 ≥ 38 mm），
    或外侧（与针杆连杆同一平面，两杆中线一转里至少隔开 14 mm）；
  - 机头里面放得下：挑线杆、摇杆的销孔和摇杆支点都在机头内腔里。
两个导线点（上面的过线钩、下面的面板导线钩）也一起找，限在机头前面的合理位置。
目标：最小传动角最大（加余量奖励），线眼加速度不超过教材机构的 1.1 倍。

    python3 tools/wqls/g4_takeup.py [差分进化代数]     → docs/设计/WQ-LS/G4/挑线机构.json、挑线机构.png
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "services" / "gateway"), str(HERE)]
from app.sewcore import design as D  # noqa: E402
from app.sewcore import kit  # noqa: E402
from app.sewcore.kit import DEG, Mech, _clamp  # noqa: E402

import spec as S  # noqa: E402



class Mech2(Mech):
    """设计软件的机构模型，挑线四杆多一个装配分支 br（+1 = 设计软件原来那一支，-1 = 另一支）。"""

    @staticmethod
    def link_pose(f, lk):
        q = (f + lk["d"]) * DEG
        P = [-lk["r"] * math.sin(q), -lk["r"] * math.cos(q)]
        Q = [lk["Qz"], lk["Qy"]]
        dz, dy = Q[0] - P[0], Q[1] - P[1]
        D_ = math.hypot(dz, dy)
        tt = (lk["a"] ** 2 - lk["b"] ** 2 + D_ * D_) / (2 * D_)
        h2 = lk["a"] ** 2 - tt * tt
        if not h2 > 0:
            return None
        h = math.sqrt(h2) * lk.get("br", 1)
        mz, my = P[0] + tt * dz / D_, P[1] + tt * dy / D_
        M = [mz - h * dy / D_, my + h * dz / D_]
        uz, uy = (M[0] - P[0]) / lk["a"], (M[1] - P[1]) / lk["a"]
        ca, sa = math.cos(lk["al"] * DEG), math.sin(lk["al"] * DEG)
        E = [P[0] + lk["c"] * (uz * ca - uy * sa), P[1] + lk["c"] * (uz * sa + uy * ca)]
        w1, w2 = [P[0] - M[0], P[1] - M[1]], [Q[0] - M[0], Q[1] - M[1]]
        mu = math.acos(_clamp((w1[0] * w2[0] + w1[1] * w2[1]) / lk["a"] / lk["b"], -1, 1)) / DEG
        return dict(P=P, M=M, E=E, Q=Q, mu=mu)

    def takeup(self, *a, **kw):
        """线路两个导线点用本机机头上的实际位置（设计软件用的是教材算例的 AC、B_GUIDE）。"""
        lk = kw.get("lk") or self.LK0
        if "A" not in lk:
            return super().takeup(*a, **kw)
        old = kit.AC, kit.B_GUIDE
        kit.AC, kit.B_GUIDE = tuple(lk["A"]), tuple(lk["B"])
        try:
            return super().takeup(*a, **kw)
        finally:
            kit.AC, kit.B_GUIDE = old


OUT = ROOT / "docs" / "设计" / "WQ-LS" / "G4"
P = D.clean(S.SEW)
PHC = round(D.analyze(P, trial=False)["key"]["fc"])
T_FAB = 1.5
HEAD_IN = dict(u=(-65.0, 43.5), v=(46 + 5 - S.ZU, 33.0))   # 顶上：机头顶内壁 z ≈ 240（FreeCAD 实测），减销座半径 7   # 机头内腔（端视 u = -Y、v = Z - ZU），前壁外 u > 48 只许线眼一头伸出去
R_CW = 34.0
ROD_CLR = 14.0              # 摇杆装在外侧（与连杆同一平面）时，摇杆中线与连杆中线至少隔开：连杆半宽 7 + 摇杆半宽 5 + 间隙 2
MARGIN_MAX = 6.0            # 余量太多：钩线时多出来的线松在旋梭周围（教材机构 1.9 mm）
SLOT = (126.0, 228.0)       # 前盖板竖槽能开的上下限（前盖板窗口 z 118–236，四周留 8 mm）


def seg_seg(A, B, C, D_):
    """两线段的最近距离（取样足够细）"""
    A, B, C, D_ = (np.asarray(x, float) for x in (A, B, C, D_))
    s = np.linspace(0, 1, 41)
    P1 = A + s[:, None] * (B - A)
    P2 = C + s[:, None] * (D_ - C)
    return float(np.min(np.linalg.norm(P1[:, None, :] - P2[None, :, :], axis=2)))


def seg_axis(A, B):
    A, B = np.asarray(A, float), np.asarray(B, float)
    d = B - A
    t = max(0.0, min(1.0, -(A @ d) / (d @ d)))
    return float(np.linalg.norm(A + t * d))


def evaluate(lk: dict) -> dict:
    m = Mech2(r=P["r"], l=P["l"], mr=P["mr"], lk=lk)
    R = m.takeup(u=P["u"], t=T_FAB, s=P["s"], phc=PHC, rpm=P["n"], lk=m.LK0)
    if not R["ok"]:
        return dict(ok=False, why="装不上（四杆不闭合）")
    Es, rock, rod, out_mm = [], 1e9, 1e9, 0.0
    for f in range(0, 360, 2):
        p = m.link_pose(f, m.LK0)
        Es.append(p["E"])
        rock = min(rock, seg_axis(p["M"], p["Q"]))
        q_ = f * DEG
        C = (P["r"] * math.sin(q_), P["r"] * math.cos(q_))
        Bv = C[1] - math.sqrt(P["l"] ** 2 - C[0] ** 2)
        rod = min(rod, seg_seg(p["M"], p["Q"], C, (0.0, Bv)))
        for k in ("P", "M", "Q"):
            u, v = p[k]
            out_mm = max(out_mm, HEAD_IN["u"][0] - u, u - HEAD_IN["u"][1], HEAD_IN["v"][0] - v, v - HEAD_IN["v"][1])
    E = np.array(Es)
    out = dict(ok=True, margin=R["margin"], neg=R["neg"], pre=R["pre"], waste=R["waste"], Smax=R["Smax"], acc=R["acc"],
               mu=R["mu"], rock=rock, rod=rod, side=lk.get("side", "in"), E_umax=float(E[:, 0].max()), E_umin=float(E[:, 0].min()),
               E_v=(float(E[:, 1].min()), float(E[:, 1].max())), out_mm=out_mm, inner=out_mm <= 0,
               guide_u=min(lk["A"][0], lk["B"][0]) if "A" in lk else 99.0, Qu=lk["Qz"])
    return out


BASE = evaluate(dict(Mech().LK0))           # 教材机构（单独挑线曲柄），只作对比
ACC_MAX = 1.1 * BASE["acc"]


def feasible(r: dict) -> list[str]:
    bad = []
    if not r["ok"]:
        return [r["why"]]
    if r["margin"] < 1:
        bad.append("余量")
    if r["margin"] > MARGIN_MAX:
        bad.append("余量太多")
    if r["E_umax"] > 85:
        bad.append("线眼伸出太远")
    if r["E_v"][1] < 0:
        bad.append("线眼最高点太低")
    if r.get("guide_u", 99) < 50:
        bad.append("导线点在机头里")
    if r.get("Qu", 0) > 35.5 and r.get("side") == "out":
        bad.append("摇杆销座出前壁")
    if r["neg"] > 1:
        bad.append("入布前缺线")
    if r["pre"] > P["stroke"]:
        bad.append("入布前多余")
    if r["E_umax"] < 58:
        bad.append("线眼伸不出")
    if not (SLOT[0] - S.ZU < r["E_v"][0] and r["E_v"][1] < SLOT[1] - S.ZU):
        bad.append("线眼出槽")
    if r["side"] == "in" and r["rock"] < R_CW + 4:
        bad.append("摇杆碰平衡块")
    if r["side"] == "out" and r["rod"] < ROD_CLR:
        bad.append("摇杆碰连杆")
    if not r["inner"]:
        bad.append("杆件出机头")
    if r["acc"] > ACC_MAX:
        bad.append("线眼加速度")
    return bad


def violation(r: dict) -> float:
    """不满足的程度（0 = 都满足），给搜索指方向。"""
    if not r["ok"]:
        return 99.0
    v = max(0, 1 - r["margin"]) + max(0, r["margin"] - MARGIN_MAX) / 2 + max(0, r["E_umax"] - 85) / 10 + max(0, -r["E_v"][1]) / 10 + max(0, r["neg"] - 1) + max(0, r["pre"] - P["stroke"]) / 2
    v += max(0, 58 - r["E_umax"]) / 10 + max(0, SLOT[0] - S.ZU - r["E_v"][0]) / 10 + max(0, r["E_v"][1] - SLOT[1] + S.ZU) / 10
    v += (max(0, R_CW + 4 - r["rock"]) if r["side"] == "in" else max(0, ROD_CLR - r["rod"])) / 5 + max(0, r["out_mm"]) / 10 + max(0, r["acc"] / ACC_MAX - 1) * 5
    return v


def lk_of(q: dict) -> dict:
    return dict(r=P["r"], d=180.0, a=q["a"], b=q["b"], c=q["c"], al=q["al"], Qz=q["Qz"], Qy=q["Qy"], br=q.get("br", 1),
                A=(q["Au"], q["Av"]), B=(q["Bu"], q["Bv"]), side=q.get("side", "in"))


KEYS = ["a", "b", "c", "al", "Qz", "Qy", "Au", "Av", "Bu", "Bv"]
BOUNDS = [(25, 70), (20, 70), (40, 100), (-60, 40), (-40, 35), (-90, 50), (50, 62), (-45, 20), (50, 62), (-115, -50)]
# Qz ≤ 35：摇杆销座（半径 8）要整个在机头前壁（u = 43.5）里面，不能伸到前盖板上


def score(x, br, side):
    """越小越好：先满足全部约束（violation），再求最小传动角大、余量适中（2–4 mm）"""
    q = dict(zip(KEYS, map(float, x)), br=br, side=side)
    r = evaluate(lk_of(q))
    if not r["ok"]:
        return 50.0
    return violation(r) - 0.002 * r["mu"][0] + 0.01 * max(0, r["margin"] - 4)


def _de_one(br, side, maxiter):
    from scipy.optimize import differential_evolution
    res = differential_evolution(score, BOUNDS, args=(br, side), seed=7, popsize=20, maxiter=maxiter, tol=1e-9, polish=False,
                                 mutation=(0.5, 1.0), recombination=0.8)
    q = dict(zip(KEYS, map(float, res.x)), br=br, side=side)
    r = evaluate(lk_of(q))
    return dict(q=q, r=r, bad=feasible(r))


def search(maxiter: int = 180, cands=None):
    """两步：①差分进化（scipy，种子固定）在两种装配分支 × 摇杆装内/外侧四种组合里各找一次；
    ②在满足约束的结果附近用 Nelder–Mead 细调，目标改为最小传动角 + 余量奖励，仍不许违反约束。
    （试过 optuna TPE 直接搜：约束太多太窄，6000 次一个可行解都没有，所以改用差分进化。）"""
    from scipy.optimize import minimize
    if cands is not None:                       # 只细调：用上次差分进化的结果（挑线机构.json 里的 candidates）
        cands = [dict(q=c["q"], r=evaluate(lk_of(c["q"])), bad=feasible(evaluate(lk_of(c["q"])))) for c in cands]
    combos = [] if cands is not None else [(1, "in"), (1, "out"), (-1, "in"), (-1, "out")]
    cands = cands or []
    if combos:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(min(len(combos), os.cpu_count() or 1)) as pool:
            for c in pool.starmap(_de_one, [(br, side, maxiter) for br, side in combos]):
                cands.append(c)
                print(c["q"]["br"], c["q"]["side"], c["bad"], round(c["r"]["mu"][0], 1) if c["r"]["ok"] else "-", flush=True)
    good = [c for c in cands if c["r"]["ok"] and violation(c["r"]) < 0.1]     # 满足或差一点满足的都细调
    for c in good:
        br, side = c["q"]["br"], c["q"]["side"]

        def obj(x):
            q = dict(zip(KEYS, map(float, x)), br=br, side=side)
            r = evaluate(lk_of(q))
            if not r["ok"]:
                return 1e3
            vb = violation(r) + max(0, r["neg"] - 0.9) + max(0, 1.2 - r["margin"])   # 细调时留余地，尺寸取整后仍满足
            if vb > 0:
                return 100 + 100 * vb
            return -(r["mu"][0] + 2 * min(r["margin"], 3)) + 3 * max(0, r["margin"] - 4)
        x0 = [min(max(c["q"][k], lo), hi) for k, (lo, hi) in zip(KEYS, BOUNDS)]
        res = minimize(obj, x0, method="Nelder-Mead", bounds=BOUNDS, options=dict(maxiter=1500, xatol=0.05, fatol=0.01))
        if res.fun < 100:                                      # 细调后满足（含余地）才换
            c["q"] = dict(zip(KEYS, map(float, res.x)), br=br, side=side)
            c["r"] = evaluate(lk_of(c["q"]))
    good = [c for c in good if not feasible(c["r"])]
    good.sort(key=lambda c: -(c["r"]["mu"][0] + 2 * min(c["r"]["margin"], 3)))
    return good, cands


def plot(lk: dict, r: dict, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for f in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"):
        if Path(f).exists():
            font_manager.fontManager.addfont(f)
            plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name()
    m = Mech2(r=P["r"], l=P["l"], mr=P["mr"], lk=lk)
    m0 = Mech()
    R = m.takeup(u=P["u"], t=T_FAB, s=P["s"], phc=PHC, rpm=P["n"], lk=m.LK0)
    R0 = m0.takeup(u=P["u"], t=T_FAB, s=P["s"], phc=PHC, rpm=P["n"], lk=m0.LK0)
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw=dict(width_ratios=[1, 1.25]))
    th = np.linspace(0, 2 * np.pi, 80)
    a.add_patch(plt.Rectangle((-43.5, 50.5 - S.ZU), 109.0, 240.3 - 50.5, fc="#f3f1ec", ec="#999", lw=0.8))   # 机头内腔（FreeCAD 实测）
    a.plot(R_CW * np.cos(th), R_CW * np.sin(th), color="#bbb", lw=0.8, ls="--")
    E = np.array([m.link_pose(f, m.LK0)["E"] for f in range(360)])
    a.plot(-E[:, 0], E[:, 1], color="#c0392b", lw=1.2, label="线眼轨迹")
    for f, al_ in ((0, 1.0), (90, 0.45), (180, 0.45), (270, 0.45)):
        p = m.link_pose(f, m.LK0)
        g = lambda k: (-p[k][0], p[k][1])  # noqa: E731
        a.plot(*zip(g("P"), g("M"), g("E"), g("P")), color="#1f6f8b", lw=2.2, alpha=al_)
        a.plot(*zip(g("M"), g("Q")), color="#555", lw=1.6, alpha=al_)
        q_ = f * math.pi / 180
        a.plot([0, -P["r"] * math.sin(q_)], [0, P["r"] * math.cos(q_)], color="#333", lw=3, alpha=al_)
    a.plot(0, 0, "o", color="#333")
    a.set_aspect("equal")
    a.set_xlabel("Y（向后为正）mm")
    a.set_ylabel("Z − 上轴中心 mm")
    a.axvline(-48, color="#999", lw=0.8)
    a.text(-49, -140, "机头前壁（前盖板）", ha="right", fontsize=9, color="#666")
    a.set_title("共用曲柄销的挑线四连杆（φ = 0°、90°、180°、270°）", fontsize=11)
    a.legend(loc="lower right", fontsize=9)
    phi = np.arange(360)
    b.plot(phi, R["S"], color="#1f6f8b", lw=1.8, label="供线（本机）")
    b.plot(phi, R["D"], color="#c0392b", lw=1.4, label="耗线")
    b.plot(phi, R0["S"], color="#1f6f8b", lw=1, ls="--", alpha=0.6, label="供线（教材机构，对比）")
    b.axvline(PHC, color="#999", lw=0.8)
    b.text(PHC + 2, 5, "钩线", fontsize=9, color="#666")
    b.set_xlim(0, 360)
    b.set_xlabel("上轴转角 φ（°）")
    b.set_ylabel("mm")
    b.set_title(f"供线与耗线：余量 {r['margin']:.1f} mm，最小传动角 {r['mu'][0]:.0f}°", fontsize=11)
    b.legend(fontsize=9)
    b.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "polish":       # python3 g4_takeup.py polish：只重做细调
        prev = json.loads((OUT / "挑线机构.json").read_text())["candidates"]
        good, cands = search(cands=prev)
    else:
        maxiter = int(sys.argv[1]) if len(sys.argv) > 1 else 180
        good, cands = search(maxiter)
    OUT.mkdir(parents=True, exist_ok=True)
    if not good:
        print("没有可行解", [c["bad"] for c in cands])
        return
    def rounded(q):
        lk_ = lk_of(q)
        return {k: (tuple(round(x, 2) for x in v) if isinstance(v, tuple) else (round(v, 2) if isinstance(v, float) else v)) for k, v in lk_.items()}
    good = [c for c in good if not feasible(evaluate(rounded(c["q"])))] or good     # 取整后仍满足的优先
    lk = lk_of(good[0]["q"])
    r = evaluate(lk)
    rnd = lambda v: round(v, 2) if isinstance(v, float) else v  # noqa: E731
    res = dict(lk={k: (tuple(round(x, 2) for x in v) if isinstance(v, tuple) else rnd(v)) for k, v in lk.items()}, result=r, baseline=BASE,
               phc=PHC, candidates=[dict(q={k: rnd(v) for k, v in c["q"].items()}, bad=c["bad"]) for c in cands])
    (OUT / "挑线机构.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    r = evaluate(res["lk"])                              # 用取整后的尺寸再算一遍（图纸上就是这些数）
    plot(res["lk"], r, OUT / "挑线机构.png")
    print(json.dumps(dict(lk=res["lk"], result=r, feasible=feasible(r)), ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
