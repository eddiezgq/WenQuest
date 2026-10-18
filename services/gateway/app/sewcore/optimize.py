# -*- coding: utf-8 -*-
"""设计优化（第 41 轮）：只用本软件公式就能算的目标，在网关里直接算（秒级，不占数字工厂计算服务）。

做法：在参数范围里随机撒点（种子固定，结果可复现），再围着最好的几个点逐步缩小范围细找；
不满足约束的点不要。每个目标返回最好的三组参数、目标值和约束，网页上“采用”一键回填。
"""
import math
import random

from .machines import get

GOALS = {
    "lockstitch": [
        ("takeup", "挑线机构：余量够的前提下传动角最大", "Take-up: largest transmission angle with enough margin"),
        ("balance", "平衡率：整机惯性力最小", "Balance ratio: smallest machine inertia force"),
        ("speed", "最高转速：不出红灯的前提下最快", "Top speed: fastest with no red checks"),
    ],
    "overlock": [
        ("lower", "下弯针：弧长 15–20 mm 时传动角最大", "Lower looper: largest transmission angle at 15–20 mm arc"),
        ("upper", "上弯针：摆角不变时传动角最大", "Upper looper: largest transmission angle at the same swing"),
        ("flat", "差动比：布边平整", "Differential ratio: flat edge"),
    ],
    "cover": [
        ("timing", "弯针定时：放在窗口正中", "Looper timing: centre of the window"),
    ],
}


def goals(machine):
    return [dict(key=k, zh=zh, en=en) for k, zh, en in GOALS.get(machine, [])]


def _search(base, spec, score, n_rand=160, n_refine=60, seed=7):
    """spec: {参数: (下限, 上限)}；score(p) 返回 (目标, 说明) 或 None（不满足约束）。目标越大越好。"""
    rnd = random.Random(seed)
    found = []

    def try_(p):
        r = score(p)
        if r is not None:
            found.append((r[0], dict(p), r[1]))
    try_(dict(base))
    for _ in range(n_rand):
        p = dict(base)
        for k, (lo, hi) in spec.items():
            p[k] = round(lo + rnd.random() * (hi - lo), 3)
        try_(p)
    for rnd_i in range(n_refine):
        if not found:
            break
        found.sort(key=lambda x: -x[0])
        _, best, _ = found[min(rnd_i % 3, len(found) - 1)]
        p = dict(best)
        shrink = 0.25 * (1 - rnd_i / n_refine) + 0.02
        for k, (lo, hi) in spec.items():
            p[k] = round(min(hi, max(lo, best[k] + (rnd.random() * 2 - 1) * (hi - lo) * shrink)), 3)
        try_(p)
    found.sort(key=lambda x: -x[0])
    out, seen = [], set()
    for v, p, note in found:
        key = tuple(round(p[k], 2) for k in spec)
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(value=v, params={k: p[k] for k in spec}, note=note))
        if len(out) == 3:
            break
    return out


def run(machine, params, goal):
    M = get(machine)
    p = M.clean(params)
    rng = {k: (M.PARAMS[k][5], M.PARAMS[k][6]) for k in M.PARAMS if k not in M.CHOICES}
    if machine == "lockstitch" and goal == "takeup":
        from .kit import Mech
        spec = {k: rng[k] for k in ("lk_r", "lk_a", "lk_b", "lk_c", "lk_al", "lk_d")}
        t = {"lining": 0.4, "cotton": 1.5, "denim": 4.0}[p["fab"]]
        mech0 = M.mech_of(p)
        phc = int(math.floor(mech0.PHC0 + p["psi"] / 2 + 0.5))

        def score(q):
            lk = dict(r=q["lk_r"], a=q["lk_a"], b=q["lk_b"], c=q["lk_c"], al=q["lk_al"], d=q["lk_d"])
            mm = Mech(r=q["r"], l=q["l"], mr=q["mr"], lk=lk)
            R = mm.takeup(u=q["u"], t=t, s=q["s"], phc=phc, rpm=q["n"], lk=mm.LK0)
            if not R["ok"] or R["margin"] < 1 or R["neg"] > 1 or R["pre"] > q["stroke"]:
                return None
            return R["mu"][0] + 0.5 * min(R["margin"], 4), dict(mu_min=round(R["mu"][0], 1), margin=round(R["margin"], 2),
                                                                pre=round(R["pre"], 1), neg=round(R["neg"], 2))
        res = _search(p, spec, score)
        unit = ("传动角 + 余量加分", "angle + margin bonus")
    elif machine == "lockstitch" and goal == "balance":
        mech = M.mech_of(p)
        rows = []
        for i in range(101):
            k = i / 100
            fmax = max(math.hypot(x, y) for x, y in mech.forces(n=p["n"], k=k, dT=p["dT"]))
            rows.append((-fmax, {"k": k}, dict(fmax=round(fmax, 1))))
        rows.sort(key=lambda x: -x[0])
        res = [dict(value=v, params=q, note=nt) for v, q, nt in rows[:3]]
        unit = ("−整机惯性力 N", "−inertia force N")
    elif machine == "lockstitch" and goal == "speed":
        lo, hi = M.PARAMS["n"][5], M.PARAMS["n"][6]
        ok = lambda n: M.analyze(dict(p, n=n), trial=False)["ok"]  # noqa: E731
        best = None
        for n in range(int(lo), int(hi) + 1, 100):
            if ok(n):
                best = n
        res = [dict(value=best, params={"n": best}, note={})] if best else []
        unit = ("r/min", "r/min")
    elif machine == "overlock" and goal in ("lower", "upper"):
        from . import overlock as O
        if goal == "lower":
            spec = {k: rng[k] for k in ("ll_r", "ll_b", "ll_c")}

            def score(q):
                R = O.rssr(q["ll_r"], q["ll_b"], q["ll_c"], O.LL, q["n"])
                if R["fail"]:
                    return None
                arc = R["swing"] * math.pi / 180 * q["ll_R"]
                if not 15 <= arc <= 20:
                    return None
                rc = O.r_critical(q["ll_b"], q["ll_c"], O.LL, lo=2.0)
                if q["ll_r"] > 0.7 * rc:
                    return None
                return R["gmin"], dict(gamma_min=round(R["gmin"], 1), swing=round(R["swing"], 2), arc=round(arc, 1))
        else:
            spec = {k: rng[k] for k in ("ul_r", "ul_b", "ul_c")}
            U0 = O.rssr(p["ul_r"], p["ul_b"], p["ul_c"], O.UL, p["n"])
            sw0 = U0.get("swing")

            def score(q):
                R = O.rssr(q["ul_r"], q["ul_b"], q["ul_c"], O.UL, q["n"])
                if R["fail"] or sw0 is None or abs(R["swing"] - sw0) > 1.0:
                    return None
                return R["gmin"], dict(gamma_min=round(R["gmin"], 1), swing=round(R["swing"], 2))
        res = _search(p, spec, score)
        unit = ("最小传动角 °", "min. transmission angle °")
    elif machine == "overlock" and goal == "flat":
        from . import overlock as O
        D = round(O.diff_feed(p["fab"], 1.0, p["pf"], p["s"])["dstar"], 2)
        e = O.diff_feed(p["fab"], D, p["pf"], p["s"])["eps"]
        res = [dict(value=-abs(e), params={"D": D}, note=dict(eps_pct=round(e * 100, 2)))]
        unit = ("−|ε|", "−|ε|")
    elif machine == "cover" and goal == "timing":
        from . import cover as C
        st = {k: p[k] for k in ("dphi", "dz", "e", "gap", "rr")}
        win = [d / 2 for d in range(-30, 31) if all(C.evaluate(dict(st, dphi=d / 2))["ok"])]
        res = [dict(value=(win[-1] - win[0]) / 2, params={"dphi": math.floor((win[0] + win[-1]) / 2 * 2 + 0.5) / 2}, note=dict(window=[win[0], win[-1]]))] if win else []
        unit = ("离窗口边缘 °", "margin to edges °")
    else:
        raise ValueError("no such goal")
    # 每组候选再整体校核一次（红灯数），网页上一起显示
    for r in res:
        R = M.analyze(dict(p, **r["params"]), trial=False)
        r["bad"] = sum(1 for c in R["checks"] if c["state"] == "bad")
        r["warn"] = sum(1 for c in R["checks"] if c["state"] == "warn")
        r["value"] = round(r["value"], 3) if isinstance(r["value"], float) else r["value"]
    return dict(machine=machine, goal=goal, unit=dict(zh=unit[0], en=unit[1]), current={k: p[k] for c in res[:1] for k in c["params"]},
                candidates=res)
