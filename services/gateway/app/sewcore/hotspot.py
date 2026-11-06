# -*- coding: utf-8 -*-
"""第 94 轮：红黄灯 → 出问题的部件、停在哪个转角 / 哪一针 / 哪一趟。

原来写在网页版讲解片里（sewing_video.py、sewing_video_seq.py），挪到计算核心，FreeCAD 工作台（安装包只带计算核心）
“校核结果”双击一行、三维标红也用这一份，两边停的地方一致。
"""
from __future__ import annotations

from . import cad, get

# ---------- 主轴机型（平缝、包缝、绷缝）----------
OL_LL = ["LL_Eccentric", "LL_BallA", "LL_BallB", "LL_Link", "LL_Rocker", "LL_Shaft", "LL_Looper"]
OL_UL = ["UL_Eccentric", "UL_BallA", "UL_BallB", "UL_Link", "UL_Rocker", "UL_Shaft"]
CV_PROBLEM = {"loop_rise": "catch", "point_h": "catch", "gap": "catch", "timing_margin": "catch", "descend": "fd", "avoid": "fd"}
# 校核项 → 出问题的机构（组）、慢放到哪个主轴转角附近（None = 整圈）
LOCK_PROBLEM = {"needle_force": ("needle", 180), "lambda": ("needle", None), "catch_rise": ("hook", "catch"), "hook": ("hook", "catch"),
                "chain": ("hook", "catch"), "frame_force": ("all", None), "frame_res": ("all", None)}
OL_PROBLEM = {"feed_window": "feed", "lambda": "needle", "diff": "feed", "diff_range": "feed", "knife_time": "knife", "knife_ov": "knife"}

# ---------- 按针 / 按趟走的机型（花样、刺绣、横机，第 89 轮）----------
# 校核项 → (出问题的组, 停在哪一针 / 哪一趟："worst" 最紧的、"far" 超行程最远的、"over" 第一条超 DST 上限的、"first_x" 第一个翻针趟、
#          "widest" 最宽的一趟、None = 不对到某一针，整机看一会儿)
PROBLEM = {
    "pattern": {"speed": (["needle", "tpl"], "worst"), "margin": (["needle"], "worst"), "head": (["head", "needle"], "worst"),
                "x_peak": (["x"], "worst"), "x_rms": (["x"], "worst"), "x_rpm": (["x"], "worst"),
                "y_peak": (["y"], "worst"), "y_rms": (["y"], "worst"), "y_rpm": (["y"], "worst"),
                "belt_x": (["x"], "worst"), "belt_y": (["y"], "worst"), "belt_dx": (["x"], "worst"),
                "travel": (["tpl", "x", "y"], "far"), "avg": (["tpl", "stitch"], None)},
    "embroid": {"accel": (["hoop", "x", "y"], "worst"), "dst": (["hoop", "stitch"], "over"), "head": (["head", "needle"], "worst"),
                "travel": (["hoop", "x", "y"], None)},
    "flatknit": {"rack": (["bed"], "first_x"), "brake": (["carriage", "drive"], "widest"), "sel_time": (["carriage"], "widest"),
                 "sel_err": (["carriage"], "widest"), "cam_res": (["carriage"], "widest"), "meas": (["carriage"], "widest"),
                 "m_peak": (["drive"], "widest"), "m_rms": (["drive"], "widest"), "m_rpm": (["drive"], "widest"),
                 "bed": (["fabric", "bed"], "widest")},
}
SEQ = tuple(PROBLEM)


def avoid_angle(M, p: dict) -> float | None:
    """绷缝机“针在弯针平面下方时不相碰”不合格时，间隙最小的转角（后侧在针回升时、前侧在针下行时；同 cover.evaluate 的扫法）"""
    st = {k: p[k] for k in ("dphi", "dz", "e", "gap", "rr")}
    E = M.evaluate(st)
    worst = []
    f = 0.0
    while f < 360:
        if M.ztip(f) <= E["zb"]:
            x, y = E["looper"](f)
            if x <= 0:
                back = 180 <= f <= E["fu"]
                c = (-y - M.RN) if back else (y - M.RN - 0.05)
                worst.append((c, f))
        f += 0.25
    return min(worst)[1] if worst else None


def catch_fd(machine: str, p: dict) -> tuple[float | None, float | None]:
    """钩线角（平缝机：旋梭尖钩线；绷缝机：弯针钩线）、绷缝机针下到弯针平面的转角"""
    if machine == "lockstitch":
        from . import design
        mech = design.mech_of(p)
        return round(mech.PHC0 + p["psi"] / 2, 1), None
    if machine == "cover":
        E = get("cover").evaluate({k: p[k] for k in ("dphi", "dz", "e", "gap", "rr")})
        return round(E["fc"], 1), round(E["fd"], 1)
    return None, None


def problem_target(machine: str, key: str, catch: float, fd: float | None = None,
                   avoid_at: float | None = None) -> tuple[list[str], float | None]:
    """红黄灯项 → 要透视的组、慢放的转角（绷缝机：钩线角或针下到弯针平面的转角）"""
    if machine == "cover":
        k = CV_PROBLEM.get(key)
        if key == "avoid" and fd is not None and avoid_at is not None:   # 不相碰：慢放到间隙最小（出问题）的那一侧
            return ["needle", "looper"], avoid_at
        if k == "catch":
            return ["needle", "looper", "thread"], catch
        if k == "fd":
            return ["needle", "looper"], fd
        return ["looper"], None
    if machine == "lockstitch":
        if key.startswith("takeup") or key.startswith("tension"):
            return ["takeup"], None
        if key.startswith("feed"):
            return ["feed", "frame"], None
        g, phi = LOCK_PROBLEM.get(key, ("all", None))
        return (["needle", "takeup", "hook", "feed", "drive"] if g == "all" else [g]), (catch if phi == "catch" else phi)
    if key.startswith("ll_"):
        return list(OL_LL), None
    if key.startswith("ul_"):
        return list(OL_UL), None
    return [OL_PROBLEM.get(key, "needle")], None


def names_in(machine: str, params: dict, groups: list[str]) -> list[str]:
    """组名可以是机构名（needle……）也可以是零件名；返回零件名清单"""
    names = [q["name"] for q in cad.parts3d(params, 0.0, machine)["parts"]]
    return [n for n in names if n in groups or cad.group_of(n) in groups]


def seq_target(machine: str, D: dict, how: str | None) -> int | None:
    """按针 / 按趟走的机型：停在第几针 / 第几趟（D = cad_seq.video_track 的轨迹）"""
    if how is None:
        return None
    k = D.get(how)
    if k is None:
        return None
    return max(0, min(D["n"] - 1, int(k)))


def seq_how(machine: str, c: dict) -> tuple[list[str], str | None]:
    grp, how = PROBLEM[machine].get(c["key"], ([], None))
    if how in ("far", "over") and c["state"] != "bad":      # 同样机的 goBad：超行程、超 DST 上限亮红灯时才去那一针，否则看最紧的一针
        how = "worst"
    return grp, how


def seq_slow(machine: str, D: dict):
    """第 k 针慢放从哪个进度角开始、慢放多少度（讲解片“停下慢放”和 FreeCAD 双击停的地方都按它）"""
    if machine == "pattern":
        f1, f2 = D["f1"], D["f2"]
        return (lambda k: (k - 1) * 360 + f2 - 25), 360 - (f2 - f1) + 60     # 出布前一点，看完整个移动
    if machine == "embroid":
        W = D["W"]
        return (lambda k: (k - 1) * 360 + 360 - W / 2 - 30), W + 150          # 窗口开始前一点
    return (lambda k: k * 360), 360                                           # 横机：整一趟


def seq_stop(machine: str, D: dict, k: int) -> float:
    """停在第 k 针 / 趟时的进度角：慢放那一段的正中（讲解片这一段的关键画面也在正中）"""
    lo = 1 if machine != "flatknit" else 0
    k = max(lo, k)
    start, span = seq_slow(machine, D)
    return round(max(0.0, start(k) + span / 2), 1)


def hotspots(machine: str, params: dict | None = None, R: dict | None = None) -> list[dict]:
    """全部红黄灯项（先红后黄）：{key, state, name, groups, names, phi, index}。
    phi：停在哪个主轴转角（花样、刺绣、横机是进度角）；None = 不对到某个转角，只标红。index：第几针 / 第几趟（从 0 数，按全部针数；主轴机型为 None）。
    whole：整机的项（机壳共振、整机惯性力）——FreeCAD 不涂色（不然整台都红，看不出是哪个机构），双击时选中全部机构。"""
    M = get(machine)
    p = M.clean(params or {})
    if R is None:
        R = M.analyze(p)
    bad = [c for c in R["checks"] if c["state"] == "bad"] + [c for c in R["checks"] if c["state"] == "warn"]
    out = []
    if not bad:
        return out
    if machine in SEQ:
        from . import cad_seq as CS
        D = CS.cfg_of(machine, p)[0]          # 全部针（讲解片抽样过；抽样时出问题的那一针和前一针都留着，停的是同一针）
        lo = 1 if machine != "flatknit" else 0
        for c in bad:
            grp, how = seq_how(machine, c)
            k = seq_target(machine, D, how) if D["n"] > lo else None
            phi = seq_stop(machine, D, k) if k is not None else None
            if k is not None:
                k = max(lo, k)
                idx = D["idx"][k] if D.get("idx") else k         # 样机数据本身可能抽样过：idx 是真正的第几针 / 趟
            out.append(dict(key=c["key"], state=c["state"], name=c.get("name"), groups=list(grp),
                            names=names_in(machine, p, grp), phi=phi, index=(None if k is None else idx), whole=False))
        return out
    catch, fd = catch_fd(machine, p)
    av = avoid_angle(M, p) if machine == "cover" else None
    for c in bad:
        groups, phi = problem_target(machine, c["key"], catch, fd, av)
        whole = machine == "lockstitch" and LOCK_PROBLEM.get(c["key"], ("", None))[0] == "all"
        out.append(dict(key=c["key"], state=c["state"], name=c.get("name"), groups=list(groups),
                        names=names_in(machine, p, groups), phi=phi, index=None, whole=whole))
    return out
