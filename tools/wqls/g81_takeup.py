"""G8.1 第三步：挑线四连杆按三维线路、三种布厚重新综合（Eddie 2026-11-17 定）。

为什么：G8.1 运动学（g81_kin.py）查出 G4 的挑线机构①只按端视算线长，三维里过线点 A、B 和线眼不在同一平面，挑线量少 10 mm；
②只按棉布 1.5 算，任务书的轻牛仔四层（3.0）余量 0.2、入布后欠线 3.9，不够。
做法：沿用 g4_takeup.py 的搜索和全部实体约束，只换供线的算法和判据：
  - 线长 = |A − 线眼| + |线眼 − B|，三维：A 在 x XA（挑线杆右侧让开 3 mm，否则挑线簧 → A 那段线穿过挑线杆），线眼、B 在挑线杆平面 x XE；
  - 衬里 0.4、棉布 1.5、轻牛仔四层 3.0 同时满足：余量 1–6、入布后欠线 ≤ 1、入布前多余 ≤ 挑线簧行程；耗线照 sewcore Mech.demand。

    python3 tools/wqls/g81_takeup.py [差分进化代数]   → docs/设计/WQ-LS/G4/挑线机构.json（新）、G8/G8.1_挑线机构.json（新旧对照）
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE)]
import g4_takeup as T  # noqa: E402
import spec as S  # noqa: E402

XE = S.MECH_X["lever"][0] + S.MECH_X["lever"][1] / 2          # 挑线杆平面（线眼）x 21.5
XA = S.MECH_X["lever"][0] + S.MECH_X["lever"][1] + 3.0          # 过线点 A：杆右侧让开 3 → x 28.5
XB = XE
FABS = dict(lining=0.4, cotton=1.5, light_denim_x4=3.0)
S_REF = 3.0
M_TOP = 25.0           # 摇杆—挑线杆铰点 M 走到前壁附近（u ≥ 36）时不得高过 v 25（z 225）：铰点处杆端半径约 6，
                       # 前盖板窗口上沿 z 234（外观 B）带圆角，第一次综合出来 M 到 v 27.4，挑线杆、摇杆碰窗口上沿（三维干涉 0 / 0.66 mm）
MU_MAX = 140.0          # G1 判据：挑线四杆传动角 40°–140°（G4 只限了下限；第一次搜出来上限 172°，接近死点）
OUT8 = T.ROOT / "docs" / "设计" / "WQ-LS" / "G8"
_M = T.Mech2(r=T.P["r"], l=T.P["l"], mr=T.P["mr"])
_DRAW = {t: np.array([_M.demand(i, t, S_REF, T.PHC) for i in range(360)]) for t in FABS.values()}   # 只和布厚、钩线角有关
_EYE_TDC = _M.EYE_TDC
_XN = np.array([_M.xN(i) for i in range(360)])


def takeup3d(lk: dict, t: float):
    """同 sewcore Mech.takeup 的判据，线长换成三维"""
    A, B = lk["A"], lk["B"]
    Lp, E, mu = [], [], []
    for i in range(360):
        p = T.Mech2.link_pose(i, lk)
        if not p:
            return None
        e = p["E"]
        E.append(e)
        mu.append(p["mu"])
        Lp.append(math.sqrt((XA - XE) ** 2 + (e[0] - A[0]) ** 2 + (e[1] - A[1]) ** 2)
                  + math.sqrt((XB - XE) ** 2 + (e[0] - B[0]) ** 2 + (e[1] - B[1]) ** 2))
    Lp = np.array(Lp)
    Sp = Lp.max() - Lp
    top = int(np.argmin(Sp))
    c = S_REF + t
    D = np.where(np.arange(360) < top, c, _DRAW[t])
    sl = Sp - D
    phc = T.PHC
    fin = int(np.argmax(_XN >= _EYE_TDC - t))
    margin = float(sl[phc:min(359, phc + 135) + 1].min())
    pre = float(sl[top:fin + 1].max()) if fin >= top else -1e9
    neg = float(max(0.0, (-sl[fin:phc]).max())) if phc > fin else 0.0
    return dict(margin=margin, neg=neg, pre=pre, Smax=float(Sp.max()), top=top, mu=[min(mu), max(mu)], E=E, Sp=Sp, D=D)


_eval2d = T.evaluate


def evaluate(lk: dict) -> dict:
    base = _eval2d(lk)                               # 实体约束（摇杆、连杆、机头内腔、线眼位置、端视加速度）照 G4
    if not base["ok"]:
        return base
    per = {}
    for k, t in FABS.items():
        R = takeup3d(lk, t)
        if R is None:
            return dict(ok=False, why="装不上（四杆不闭合）")
        per[k] = {x: R[x] for x in ("margin", "neg", "pre", "Smax", "top")}
    mtop = max((p_["M"][1] for p_ in (T.Mech2.link_pose(i, lk) for i in range(0, 360, 2)) if p_["M"][0] >= 36.0), default=-99.0)
    base.update(m_top=mtop, margin=min(v["margin"] for v in per.values()), margin_hi=max(v["margin"] for v in per.values()),
                neg=max(v["neg"] for v in per.values()), pre=max(v["pre"] for v in per.values()),
                Smax=per["cotton"]["Smax"], per_fabric=per, guide_x=dict(A=XA, eye=XE, B=XB))
    return base


_feas2d, _viol2d = T.feasible, T.violation


def feasible(r: dict) -> list[str]:
    bad = _feas2d(r)
    if r.get("ok") and r["margin_hi"] > T.MARGIN_MAX:
        bad.append("薄料余量太多")
    if r.get("ok") and r["mu"][1] > MU_MAX:
        bad.append("传动角太大")
    if r.get("ok") and r["m_top"] > M_TOP:
        bad.append("铰点碰窗口上沿")
    return bad


def violation(r: dict) -> float:
    v = _viol2d(r)
    if r.get("ok"):
        v += max(0, r["margin_hi"] - T.MARGIN_MAX) / 2 + max(0, r["mu"][1] - MU_MAX) / 10 + max(0, r["m_top"] - M_TOP) / 2
    return v


T.evaluate, T.feasible, T.violation = evaluate, feasible, violation


def plot3(lk_old, lk_new, path):
    """三种布厚的供线（三维）与耗线：G4 原机构 vs 新机构"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    f_ = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    if Path(f_).exists():
        font_manager.fontManager.addfont(f_)
    plt.rcParams.update({"font.family": ["Noto Sans CJK JP", "DejaVu Sans"], "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    cols = dict(lining="#2e9e6a", cotton="#1f5fa8", light_denim_x4="#c8102e")
    names = dict(lining="衬里 0.4", cotton="棉布 1.5", light_denim_x4="轻牛仔四层 3.0")
    for a, (title, lk_) in zip(ax, (("G4 原机构（三维线路）", lk_old), ("G8.1 新机构", lk_new))):
        lk_ = dict(lk_, A=tuple(lk_["A"]), B=tuple(lk_["B"]))
        R = None
        for k, t in FABS.items():
            R = takeup3d(lk_, t)
            a.plot(range(360), R["D"], color=cols[k], lw=1.1, ls="--", label=f"耗线 {names[k]}（余量 {R['margin']:.1f}，欠线 {R['neg']:.1f}）")
        a.plot(range(360), R["Sp"], color="#1d2733", lw=1.8, label=f"供线（挑线量 {R['Smax']:.1f}）")
        a.axvline(T.PHC, color="#7a8794", lw=0.6, ls=":")
        a.set_title(title, loc="left")
        a.set_xlabel("上轴转角 φ（°）")
        a.set_xticks(range(0, 361, 60))
        a.legend(fontsize=7, frameon=False, loc="upper left")
    ax[0].set_ylabel("mm")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main():
    old = json.loads((T.OUT / "挑线机构.json").read_text())
    old_r = evaluate(dict(old["lk"], A=tuple(old["lk"]["A"]), B=tuple(old["lk"]["B"])))
    maxiter = int(sys.argv[1]) if len(sys.argv) > 1 else 180
    good, cands = T.search(maxiter)
    if not good:
        print("没有可行解", [c["bad"] for c in cands])
        (OUT8 / "G8.1_挑线机构.json").write_text(json.dumps(dict(ok=False, old=old_r, candidates=[dict(q=c["q"], bad=c["bad"]) for c in cands]),
                                                     ensure_ascii=False, indent=1, default=float))
        return

    def rounded(q):
        lk_ = T.lk_of(q)
        return {k: (tuple(round(x, 2) for x in v) if isinstance(v, tuple) else (round(v, 2) if isinstance(v, float) else v)) for k, v in lk_.items()}
    good = [c for c in good if not feasible(evaluate(rounded(c["q"])))] or good
    lk = rounded(good[0]["q"])
    lk.update(xA=XA, xE=XE, xB=XB)
    r = evaluate(lk)
    rnd = lambda v: round(v, 2) if isinstance(v, float) else v  # noqa: E731
    new = dict(lk=lk, result=r, baseline=old["baseline"], phc=T.PHC, fabrics=FABS, method="G8.1 g81_takeup.py：三维线路、三种布厚",
               candidates=[dict(q={k: rnd(v) for k, v in c["q"].items()}, bad=c["bad"]) for c in cands], previous_G4=old["lk"])
    (T.OUT / "挑线机构.json").write_text(json.dumps(new, ensure_ascii=False, indent=1, default=float))
    T.plot(lk, r, T.OUT / "挑线机构.png")          # 左：杆件与线眼轨迹（右边的供线曲线是端视、棉布，只作 G4 格式的对照）
    plot3(old["lk"], lk, OUT8 / "G8.1_挑线供线.png")
    (OUT8 / "G8.1_挑线机构.json").write_text(json.dumps(dict(ok=not feasible(r), old_lk=old["lk"], old=old_r, new_lk=lk, new=r, bad=feasible(r)),
                                                 ensure_ascii=False, indent=1, default=float))
    print(json.dumps(dict(old=old["lk"], new=lk, per_fabric_old=old_r.get("per_fabric"), per_fabric_new=r["per_fabric"], mu=r["mu"],
                          feasible=feasible(r)), ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
