"""花样机、刺绣机、横机的三维讲解片场景（第 89 轮）。sewing_video.scene() 遇到这三种机型就交给这里写。

这三种讲“一个花样 / 一片衣片怎么走完”：进度角每 360° = 一针（花样机、刺绣机）/ 一趟（横机），零件见 sewcore/cad_seq.py。
段落：整机 → ① 一针（一趟）慢放讲清楚 → ② 移动（两轴 / 绷架 / 机头一趟）→ ③ 走一遍（快放；横机每隔若干趟看一趟）——
快放途中在“最紧的一针”（花样机：转速上限最低；刺绣机：所需加速度最大；横机：最宽的一趟）和红黄灯项对应的那一针 / 那一趟停下慢放 → 结论。
出问题的那一针 / 那一趟同第 81 轮样机的“慢放到出问题的那一针 / 那一趟”。字幕里的数全由 analyze 的结果、校核项给。
"""
import math
from typing import Any

from .sewcore import cad
from .sewcore import cad_seq as CS

S = 0.001
MACHINES = CS.MACHINES

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
UNIT = {"pattern": ("针", "stitch"), "embroid": ("针", "stitch"), "flatknit": ("趟", "pass")}


def _short(s: str, n: int) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def _join(parts: list[str], n: int) -> str:
    out = ""
    parts = [x for x in parts if x] or [""]
    for x in parts:
        y = x if not out else out + " · " + x
        if len(y) > n:
            break
        out = y
    return out or _short(parts[0], n)


def _res(R: dict, name: str, lang: str = "zh") -> str:
    """结果表里中文名以 name 开头的那一行（“名 值 单位”）；没有就空（有花样文件时结果表多几行，不能按位置取）"""
    r = next((x for x in R["results"] if x["zh"].startswith(name)), None)
    if r is None:
        return ""
    return f"{r[lang]} {r['value']}{(' ' + r['unit']) if r['unit'] else ''}"


def _box(machine: str, p: dict, phi: float, groups: list[str] | None) -> tuple[list[float], float]:
    """这些组的零件在进度角 phi 时的范围：中心（米）、对角线长（米）"""
    lo, hi = [1e9] * 3, [-1e9] * 3
    for q in cad.parts3d(p, phi, machine)["parts"]:
        if groups is not None and cad.group_of(q["name"]) not in groups:
            continue
        pts = []
        if q["type"] == "box":
            pts += [q["base"], [q["base"][i] + q["size"][i] for i in range(3)]]
        elif q["type"] == "cyl":
            pts += [q["base"], [q["base"][i] + q["dir"][i] * q["h"] for i in range(3)]]
        elif q["type"] == "sphere":
            pts.append(q["c"])
        elif q["type"] == "tube":
            pts += q["pts"]
        elif q["type"] == "plate":
            f = q["frame"]
            for x, z, _ in q["circles"]:
                pts.append([f["o"][i] + x * f["u"][i] + z * f["v"][i] for i in range(3)])
        r = q.get("r", 0) if q["type"] in ("cyl", "sphere") else 0
        for v in pts:
            for i in range(3):
                lo[i], hi[i] = min(lo[i], v[i] - r), max(hi[i], v[i] + r)
    diag = math.dist(lo, hi) * S
    return [round((lo[i] + hi[i]) / 2 * S, 4) for i in range(3)], diag


def _target(machine: str, D: dict, how: str | None) -> int | None:
    if how is None:
        return None
    k = D.get(how)
    if k is None:
        return None
    return max(0, min(D["n"] - 1, int(k)))


def scene_seq(machine: str, p: dict, R: dict, name_zh: str, name_en: str) -> tuple[dict[str, Any], dict]:
    """返回 (场景 spec, 摘要)；spec 的 panel 中英文两种都写着，sewing_video.scene 再按 lang 收"""
    D = CS.video_track(machine, CS.cfg_of(machine, p)[0])          # 讲解片用的轨迹（抽样到 800 以内，压缩后写进场景）
    pv = dict(spec_params(p, machine), _track=CS.pack(D))         # 场景里的模型参数：渲染器按它画，不再重算
    n = D["n"]
    uz, ue = UNIT[machine]
    t, a = 0.0, 0.0
    angle, cams, labels, effects = [[0, 0]], [], [], []
    st_whole, st_sec, st_prob = [], [], []

    def run(dt: float, deg: float):
        nonlocal t, a
        t = round(t + dt, 2)
        a = round(a + deg, 1)
        angle.append([t, a])

    def jump(to: float):
        """直接跳到进度角 to（快放时跳过中间的针 / 趟；往回跳 = 重放这一针）"""
        nonlocal t, a
        if abs(to - a) < 0.05:
            return
        t = round(t + 0.04, 2)
        a = round(to, 1)
        angle.append([t, a])

    def cam(t_, look, az, el, dist):
        cams.append({"t": round(t_, 2), "look": look, "az": az, "el": el, "dist": round(dist, 3), "lens": 40})

    def lab(t0, t1, zh, en, where=None, tone=None):
        L = {"t": [round(t0, 2), round(t1, 2)], "zh": _short(zh, 46), "en": _short(en, 120)}
        if where:
            L["where"] = where
        if tone:
            L["tone"] = tone
        labels.append(L)

    def xray(t0, t1, groups):
        effects.append({"kind": "xray", "t": [round(t0, 2), round(t1, 2)], "top": [f"d.{g}" for g in groups]})

    whole_c, whole_d = _box(machine, pv, 0.0, None)
    whole_c[2] = round(whole_c[2] - 0.06 * whole_d, 4)
    dist_whole = max(0.25, 1.9 * whole_d)
    # ---------- 1 整机
    cam(0, whole_c, -40, 20, dist_whole)
    cam(5.5, whole_c, -22, 16, dist_whole * 0.92)
    if machine == "pattern":
        head = (f"这台{name_zh}：花样 {D['N']} 针，设计 {p['n']:g} r/min", f"This {name_en.lower()} machine: {D['N']} stitches, {p['n']:g} r/min")
    elif machine == "embroid":
        more = f"（画 {CS.EMB_HEADS} 个）" if D["H"] > CS.EMB_HEADS else ""
        head = (f"这台{name_zh}：{D['H']} 头{more}，{D['N']} 条记录，{p['n']:g} r/min",
                f"This {name_en.lower()} machine: {D['H']} heads, {D['N']} records, {p['n']:g} r/min")
    else:
        head = (f"这台{name_zh}：一片 {D['N']} 趟，{D['sys']:g} 个系统", f"This {name_en.lower()} machine: {D['N']} passes per piece, {D['sys']:g} system(s)")
    lab(0, 6, *head)
    lab(0, 6, "运动、针迹、趟次按你的设计算；机构尺寸为示意", "Motion, stitches and passes follow your design; mechanism sizes are illustrative", "bottom")
    st_whole.append(3.0)
    run(6, 360 if machine == "flatknit" else 720)
    # ---------- 2 各段
    if machine == "pattern":
        f1, f2 = D["f1"], D["f2"]
        # ① 刺布与窗口：一针慢放，镜头对着针和模板
        t0 = t
        cam(t0 + 0.8, [0.0, 0.0, 0.01], -50, 16, 0.42)
        cam(t0 + 8, [0.0, 0.0, 0.01], -32, 12, 0.42)
        xray(t0 + 0.5, t0 + 8.5, ["needle", "tpl", "stitch"])
        lab(t0, t0 + 9, "① 刺布：针在布中模板不动，离布窗口里移到下一针", "① Needle: the template stands still while the needle is in")
        lab(t0, t0 + 9, _join([_res(R, "入布角"), _res(R, "离布窗口")], 46), _join([_res(R, "入布角", "en"), _res(R, "离布窗口", "en")], 110), "bottom")
        jump(math.floor(a / 360) * 360 + 360)
        run(9, 360)
        st_sec.append(round(t0 + 4.5, 2))
        # ② X、Y 两轴：再走两针，镜头拉到两轴
        t0 = t
        c, dg = _box(machine, pv, a, ["x", "y", "tpl"])
        cam(t0 + 0.8, c, -30, 30, max(0.5, 1.6 * dg))
        cam(t0 + 7, c, -15, 26, max(0.5, 1.5 * dg))
        xray(t0 + 0.5, t0 + 7.5, ["x", "y"])
        lab(t0, t0 + 8, "② X、Y 两轴：横梁带 X 轴前后走，滑座带压框左右走", "② X and Y axes: the beam carries X, the slide carries the clamp")
        lab(t0, t0 + 8, _join([_res(R, "X 轴峰值"), _res(R, "Y 轴峰值")], 46), _join([_res(R, "X 轴峰值", "en"), _res(R, "Y 轴峰值", "en")], 110), "bottom")
        run(8, 720)
        st_sec.append(round(t0 + 4, 2))
        fast_title = ("③ 走一遍花样（快放）", "③ The whole pattern (fast)")
        fast_cap = (_join([_res(R, "花样针数"), _res(R, "缝制用时")], 46), _join([_res(R, "花样针数", "en"), _res(R, "缝制用时", "en")], 110))
        tight = ("④ 最紧的一针：转速上限 {cap} r/min，这一针 {sp} r/min", "④ The tightest stitch: limit {cap} r/min, run at {sp} r/min")
        slow_from = lambda k: (k - 1) * 360 + f2 - 25                               # noqa: E731  出布前一点，看完整个移动
        slow_span = 360 - (f2 - f1) + 60
        top_view = (-20, 58)
        fast_groups = ["tpl", "stitch"]
    elif machine == "embroid":
        W = D["W"]
        h0 = cad.parts3d(pv, 0.0, "embroid")
        x0 = -((h0["heads"] - 1) * 420) / 2 + 10
        close = [round(x0 * S, 4), -0.132, 0.01]
        t0 = t
        cam(t0 + 0.8, close, -48, 16, 0.5)
        cam(t0 + 8, close, -30, 12, 0.5)
        xray(t0 + 0.5, t0 + 8.5, ["needle", "hoop", "stitch"])
        lab(t0, t0 + 9, "① 刺布：几个头一起扎，针在布中时绷架停住", "① Needles: all heads stitch together; the frame stops while they are in")
        lab(t0, t0 + 9, _join([_res(R, "可用加速度"), _res(R, "最长针的转速上限")], 46), _join([_res(R, "可用加速度", "en"), _res(R, "最长针的转速上限", "en")], 110), "bottom")
        jump(math.floor(a / 360) * 360 + 360)
        run(9, 360)
        st_sec.append(round(t0 + 4.5, 2))
        t0 = t
        c, dg = _box(machine, pv, a, ["hoop", "x", "y"])
        cam(t0 + 0.8, c, -30, 34, max(0.6, 1.3 * dg))
        cam(t0 + 7, c, -15, 30, max(0.6, 1.25 * dg))
        xray(t0 + 0.5, t0 + 7.5, ["hoop", "x", "y"])
        lab(t0, t0 + 8, "② 绷架移动：X、Y 两轴带着所有绣框一起走", "② Frame drive: X and Y move every hoop together")
        lab(t0, t0 + 8, _join([_res(R, "绷架折算质量"), _res(R, "绷架伺服")], 46), _join([_res(R, "绷架折算质量", "en"), _res(R, "绷架伺服", "en")], 110), "bottom")
        run(8, 720)
        st_sec.append(round(t0 + 4, 2))
        fast_title = ("③ 绣一遍（快放，按颜色分色）", "③ The whole design (fast, by colour)")
        fast_cap = (_join([_res(R, "纯缝纫时间"), _res(R, "全机效率")], 46), _join([_res(R, "纯缝纫时间", "en"), _res(R, "全机效率", "en")], 110))
        tight = ("④ 最难的一针：所需 / 可用加速度 {acc}", "④ The hardest stitch: required / available acceleration {acc}")
        slow_from = lambda k: (k - 1) * 360 + 360 - W / 2 - 30                      # noqa: E731  窗口开始前一点
        slow_span = W + 150
        top_view = (-20, 55)
        fast_groups = ["hoop", "stitch"]
    else:
        # ① 三角起针：一趟慢放，镜头对着针床口
        t0 = t
        cam(t0 + 0.8, [0.0, 0.0, 0.0], -24, 58, 0.95)
        cam(t0 + 8, [0.0, 0.0, 0.0], -8, 54, 0.95)
        xray(t0 + 0.5, t0 + 8.5, ["needles", "carriage"])
        lab(t0, t0 + 9, "① 三角起针：机头经过时针一根根升起又落下", "① Cams: needles rise and fall as the carriage passes")
        lab(t0, t0 + 9, _join([_res(R, "针距 / 每枚针"), _res(R, "选针器允许")], 46), _join([_res(R, "针距 / 每枚针", "en"), _res(R, "选针器允许", "en")], 110), "bottom")
        run(9, 360)
        st_sec.append(round(t0 + 4.5, 2))
        # ② 机头一趟：加速、匀速、减速、换向停顿
        t0 = t
        cam(t0 + 0.8, whole_c, -8, 22, dist_whole * 0.7)
        cam(t0 + 6, whole_c, 8, 22, dist_whole * 0.7)
        xray(t0 + 0.5, t0 + 6.5, ["carriage", "drive", "yarn"])
        lab(t0, t0 + 7, "② 机头一趟：加速、匀速、减速，换向时停一下", "② One pass: accelerate, cruise, decelerate, dwell at reversal")
        lab(t0, t0 + 7, _join([_res(R, "织物宽度"), _res(R, "一趟用时"), _res(R, "换向余量")], 46), _join([_res(R, "织物宽度", "en"), _res(R, "一趟用时", "en"), _res(R, "换向余量", "en")], 110),
            "bottom")
        run(7, 360)
        st_sec.append(round(t0 + 3.5, 2))
        # ③ 翻针与摇床（有翻针趟才有）
        fx = D.get("first_x")
        if fx is not None:
            t0 = t
            cam(t0 + 0.8, [0.0, 0.0, 0.02], 150, 40, 0.8)
            cam(t0 + 7, [0.0, 0.0, 0.02], 170, 36, 0.8)
            xray(t0 + 0.5, t0 + 7.5, ["bed", "needles"])
            lab(t0, t0 + 8, "③ 翻针与摇床：后针床横移，把线圈翻到另一床", "③ Transfer and racking: the back bed shifts, loops move across")
            lab(t0, t0 + 8, _res(R, "摇床用时"), _res(R, "摇床用时", "en"), "bottom")
            jump(fx * 360)
            run(8, 360)
            st_sec.append(round(t0 + 4, 2))
        fast_title = (("④" if fx is not None else "③") + " 织一片（快放：每隔若干趟看一趟）",
                      ("④" if fx is not None else "③") + " A whole piece (fast: one pass in every few)")
        fast_cap = (_join([_res(R, "趟数"), _res(R, "每天片数")], 46), _join([_res(R, "趟数", "en"), _res(R, "每天片数", "en")], 110))
        tight = None
        fast_groups = ["fabric", "carriage"]
    # ---------- 3 走一遍：快放，途中在最紧的一针和红黄灯项停下慢放
    bad = [c for c in R["checks"] if c["state"] == "bad"] + [c for c in R["checks"] if c["state"] == "warn"]
    stops = []                                          # (第几针 / 趟, 0 = 最紧的一针、1 = 红黄灯, 校核项)
    if tight:
        stops.append((max(1, D["worst"]), 0, None))
    loose = []
    for c in bad[:3]:
        grp, how = PROBLEM[machine].get(c["key"], ([], None))
        k = _target(machine, D, how)
        if k is None:
            loose.append(c)
        else:
            stops.append((max(1, k) if machine != "flatknit" else k, 1, c))
    stops.sort(key=lambda s_: (s_[0], s_[1]))
    cur = math.floor(a / 360)
    if machine == "flatknit":
        # 横机：每隔若干趟看一趟（一趟 1.2 秒），途中的问题趟停下慢放
        marks = sorted({s_[0] for s_ in stops})
        span_end = n - 1
        picks = sorted(set(round(cur + (span_end - cur) * i / 7) for i in range(8)) | set(marks))
        prob_at = {}
        for k, kind, c in stops:
            prob_at.setdefault(k, []).append(c)
        seg = [None]

        def close_fast():
            if seg[0] is not None and t - seg[0] > 0.5:
                lab(seg[0], t, *fast_title)
                lab(seg[0], t, *fast_cap, where="bottom")
                xray(seg[0] + 0.3, t, fast_groups)
            seg[0] = None

        for k in picks:
            if k in prob_at:
                close_fast()
                for c in prob_at[k]:
                    _problem(machine, pv, D, R, c, k, locals_=dict(cam=cam, lab=lab, xray=xray, run=run, jump=jump, st=st_prob,
                                                                   now=lambda: (t, a), whole=(whole_c, dist_whole)))
                continue
            if seg[0] is None:
                seg[0] = t
                cam(t + 0.6, whole_c, -30, 18, dist_whole * 0.9)
            jump(k * 360)
            run(1.2, 360)
            if len(st_sec) < 4:
                st_sec.append(round(t - 0.6, 2))
        close_fast()
    else:
        top_c, top_d = _box(machine, pv, a, ["tpl"] if machine == "pattern" else ["hoop"])
        top_c = [0.0, round(-0.132 if machine == "embroid" else 0.0, 4), 0.0]
        if machine == "embroid":
            h0 = cad.parts3d(pv, 0.0, "embroid")
            top_c[0] = round((-((h0["heads"] - 1) * 420) / 2 + 10) * S, 4)
        top_dist = max(0.35, 2.6 * (max(D.get("w", 0) or 0, D.get("h", 0) or 0, 60) + 90) * S) if machine == "embroid" else \
            max(0.35, 2.6 * (max(max(q[0] for q in D["pts"]) - min(q[0] for q in D["pts"]),
                                   max(q[1] for q in D["pts"]) - min(q[1] for q in D["pts"])) + 90) * S)

        def fast_to(k_end: int, final: bool = False):
            """从现在快放到第 k_end 针开始慢放的地方（或走完）：用时按针数，1.5–9 秒"""
            nonlocal t
            target_a = (n - 1) * 360 + 359 if final else slow_from(k_end)
            if target_a <= a + 1:
                if target_a < a - 1:
                    jump(target_a)
                return
            nst = (target_a - a) / 360
            dt = max(1.5, min(9.0, 0.06 * nst + 1.2))
            t0_ = t
            cam(t0_ + 0.6, top_c, top_view[0], top_view[1], top_dist)
            xray(t0_ + 0.3, t0_ + dt, fast_groups)
            lab(t0_, t0_ + dt, *fast_title)
            lab(t0_, t0_ + dt, *fast_cap, where="bottom")
            run(dt, target_a - a)
            if len(st_sec) < 4:
                st_sec.append(round(t0_ + dt * 0.7, 2))

        for k, kind, c in stops:
            fast_to(k)
            if a > slow_from(k) + 1:
                jump(slow_from(k))
            t0 = t
            if kind == 0:
                if machine == "pattern":
                    title = (tight[0].format(cap=D["cap"][k], sp=D["sp"][k]), tight[1].format(cap=D["cap"][k], sp=D["sp"][k]))
                    cap_ = (_join([f"第 {D['idx'][k] + 1} 针", _res(R, "标准针距转速上限")], 46), _join([f"stitch {D['idx'][k] + 1}", _res(R, "标准针距转速上限", "en")], 110))
                else:
                    acc = f"{D['acc'][k]:.2f}"
                    title = (tight[0].format(acc=acc), tight[1].format(acc=acc))
                    cap_ = (_join([f"第 {D['idx'][k] + 1} 针，针长 {D['L'][k]:g} mm", _res(R, "可用加速度")], 46),
                            _join([f"stitch {D['idx'][k] + 1}, {D['L'][k]:g} mm long", _res(R, "可用加速度", "en")], 110))
                look = top_c if machine == "pattern" else top_c
                cam(t0 + 0.8, look, -45, 22, 0.45 if machine == "pattern" else 0.5)
                cam(t0 + 6.5, look, -28, 18, 0.45 if machine == "pattern" else 0.5)
                xray(t0 + 0.5, t0 + 7, ["needle", "tpl" if machine == "pattern" else "hoop", "stitch"])      # 针迹也留实的
                lab(t0, t0 + 7, *title)
                lab(t0, t0 + 7, *cap_, where="bottom")
                run(7, slow_span)
                st_sec.insert(0, round(t0 + 3.5, 2))
            else:
                _problem(machine, pv, D, R, c, k, locals_=dict(cam=cam, lab=lab, xray=xray, run=run, jump=jump, st=st_prob,
                                                              now=lambda: (t, a), whole=(whole_c, dist_whole), slow=(slow_from, slow_span),
                                                              close=top_c))
                t, a = angle[-1][0], angle[-1][1]
        fast_to(n - 1, final=True)
    # 不对到某一针 / 某一趟的红黄灯项：整机看一会儿（接着走）
    for c in loose:
        t0 = t
        grp = PROBLEM[machine].get(c["key"], ([], None))[0]
        cc, dg = _box(machine, pv, a, grp or None)
        cam(t0 + 0.8, cc, -45, 18, max(0.4, 1.6 * dg))
        cam(t0 + 5.5, cc, -30, 16, max(0.4, 1.6 * dg))
        if grp:
            xray(t0 + 0.5, t0 + 6, grp)
        _bad_labels(lab, c, t0, t0 + 6)
        st_prob.append(round(t0 + 3, 2))
        run(6, 360)
    # ---------- 4 结论
    t0 = t
    nb = sum(c["state"] == "bad" for c in R["checks"])
    nw = sum(c["state"] == "warn" for c in R["checks"])
    concl = ((f"全部 {len(R['checks'])} 项校核合格", f"All {len(R['checks'])} checks pass") if not nb and not nw else
             (f"{len(R['checks'])} 项校核：不合格 {nb} 项，注意 {nw} 项", f"{len(R['checks'])} checks: {nb} fail, {nw} need attention"))
    cam(t0 + 1.5, whole_c, -30, 20, dist_whole)
    cam(t0 + 6, whole_c, -45, 22, dist_whole)
    lab(t0, t0 + 6, *concl)
    lab(t0, t0 + 6, "问渠缝纫机设计软件 · 计算书、调机卡同一组参数", "WenQuest sewing design software · same parameters as report, setup card", "bottom")
    run(6, 0)
    dur = round(t, 2)
    stills = (st_whole + st_prob)[:5]
    stills += st_sec[: max(0, 5 - len(stills))] + [round(t0 + 3.0, 2)]
    # 面板
    if machine == "pattern":
        kp = thin_idx(n, 240)
        items = [{"zh": "针号", "en": "stitch", "key": "idx", "fmt": "{:5.0f}", "unit": f" / {D['N']}"},
                 {"zh": "这一针转速", "en": "speed", "key": "sp", "fmt": "{:5.0f}", "unit": " r/min"},
                 {"zh": "这一针上限", "en": "limit", "key": "cap", "fmt": "{:5.0f}", "unit": " r/min"},
                 {"zh": "针尖离针板", "en": "needle", "key": "needle", "fmt": "{:+6.1f}", "unit": " mm", "scale": 20}]
        plot = {"key": "sp", "zh": "每针转速（红：上限）", "en": "speed per stitch (red: limit)", "series": [D["sp"][k] for k in kp],
                "ref": [min(D["cap"][k], D["n_head"]) for k in kp], "cursor": "frac", "foot": "（横轴：针号）",
                "marks": [{"at": round(D["worst"] / max(1, n - 1), 4), "zh": "最紧"}]}
    elif machine == "embroid":
        kp = thin_idx(n, 240)
        items = [{"zh": "针号", "en": "record", "key": "idx", "fmt": "{:5.0f}", "unit": f" / {D['N']}"},
                 {"zh": "颜色", "en": "colour", "key": "col", "fmt": "{:3.0f}", "unit": ""},
                 {"zh": "转速", "en": "speed", "key": "sp", "fmt": "{:5.0f}", "unit": " r/min"},
                 {"zh": "所需加速度", "en": "required acc.", "key": "need", "fmt": "{:5.1f}", "unit": f" / {D['am']:g} m/s²"}]
        plot = {"key": "acc", "zh": "所需 / 可用加速度（红线 = 1）", "en": "required / available (red = 1)",
                "series": [D["acc"][k] for k in kp], "ref": [1.0] * len(kp), "cursor": "frac", "foot": "（横轴：针号）",
                "marks": [{"at": round(D["worst"] / max(1, n - 1), 4), "zh": "最难"}]}
    else:
        kp = thin_idx(n, 240)
        items = [{"zh": "第几趟", "en": "pass", "key": "idx", "fmt": "{:5.0f}", "unit": f" / {D['N']}"},
                 {"zh": "机头速度", "en": "carriage", "key": "v", "fmt": "{:5.2f}", "unit": " m/s", "scale": max(D["v"])},
                 {"zh": "机头走了", "en": "travelled", "key": "x", "fmt": "{:5.0f}", "unit": " mm"},
                 {"zh": "累计用时", "en": "total", "key": "tacc", "fmt": "{:6.1f}", "unit": " s"}]
        plot = {"key": "top", "zh": "每趟最高速度 m/s", "en": "top speed per pass", "series": [round(CS.pass_top(D, k), 3) for k in kp],
                "cursor": "frac", "foot": "（横轴：趟）", "marks": [{"at": round(D["widest"] / max(1, n - 1), 4), "zh": "最宽"}]}
    spec: dict[str, Any] = {
        "name": f"{name_zh}讲解",
        "title": {"zh": _short(f"{name_zh}怎么走完一个" + ("花样" if machine != "flatknit" else "衣片"), 40),
                  "en": _short(f"How this {name_en.lower()} machine runs " + ("a design" if machine != "flatknit" else "a piece"), 100)},
        "duration": dur, "floor": False, "clip": 0.002,
        "models": [{"id": "d", "use": "gen:sewdesign", "machine": machine, "params": pv}],
        "motion": [{"drive": "weblab", "model": "d", "angle": angle}],
        "camera": sorted(cams, key=lambda c: c["t"]), "effects": effects, "labels": labels, "stills": sorted(set(stills))[:6],
        "panel": {"kind": "readouts", "head": "读数  Readouts", "items": items, "plot": plot},
    }
    return spec, {"bad": nb, "warn": nw, "problems": [c["key"] for c in bad[:3]]}


def thin_idx(n: int, limit: int) -> list[int]:
    from .sewcore.common import thin
    return thin(n, limit)


def spec_params(p: dict, machine: str | None = None) -> dict:
    """场景里写的设计参数：列表、字典不写（同第 56 轮）；花样机、刺绣机、横机上传的文件也不写（太长，场景里带抽样后的轨迹 _track）"""
    drop = CS.FILE_KEYS if machine in MACHINES else ()
    return {k: v for k, v in p.items() if not isinstance(v, (list, dict)) and k not in drop}


def _bad_labels(lab, c, t0, t1):
    tag = ("不合格", "fails") if c["state"] == "bad" else ("注意", "check")
    lab(t0, t1, f"⚠ {tag[0]}：{c['name']['zh']}", f"⚠ {c['name']['en']} {tag[1]}", tone=c["state"])
    lab(t0, t1, _join([c["value"]["zh"], f"判据 {c['limit']['zh']}"], 46), _join([c["value"]["en"], f"criterion {c['limit']['en']}"], 110), "bottom")


def _problem(machine, pv, D, R, c, k, locals_):
    """红黄灯项：停在出问题的那一针 / 那一趟慢放，透视出问题的部件，标题标红"""
    cam, lab, xray, run, jump, st = (locals_[x] for x in ("cam", "lab", "xray", "run", "jump", "st"))
    t0, a0 = locals_["now"]()
    grp = PROBLEM[machine].get(c["key"], ([], None))[0]
    if machine == "flatknit":
        jump(k * 360)
        t0 = locals_["now"]()[0]
        whole_c, dist_whole = locals_["whole"]
        if c["key"] == "rack":
            cam(t0 + 0.8, [0.0, 0.0, 0.02], 150, 40, 0.8)
            cam(t0 + 6.5, [0.0, 0.0, 0.02], 170, 36, 0.8)
        else:
            cam(t0 + 0.8, whole_c, -12, 22, dist_whole * 0.72)
            cam(t0 + 6.5, whole_c, 8, 22, dist_whole * 0.72)
        xray(t0 + 0.5, t0 + 7, grp)
        _bad_labels(lab, c, t0, t0 + 7)
        run(7, 360)
        st.append(round(t0 + 3.5, 2))
        return
    slow_from, slow_span = locals_["slow"]
    if a0 > slow_from(k) + 1 or a0 < slow_from(k) - 1:
        jump(slow_from(k))
        t0 = locals_["now"]()[0]
    close = locals_["close"]
    if grp and set(grp) & {"x", "y"} and "needle" not in grp:
        cc, dg = _box(machine, pv, locals_["now"]()[1], grp)
        cam(t0 + 0.8, cc, -32, 30, max(0.5, 1.5 * dg))
        cam(t0 + 6.5, cc, -18, 26, max(0.5, 1.45 * dg))
    elif "head" in grp:
        cc, dg = _box(machine, pv, 0.0, ["head"])
        cam(t0 + 0.8, cc, -45, 16, max(0.4, 1.5 * dg))
        cam(t0 + 6.5, cc, -30, 14, max(0.4, 1.5 * dg))
    else:
        cam(t0 + 0.8, close, -48, 22, 0.45)
        cam(t0 + 6.5, close, -30, 18, 0.45)
    xray(t0 + 0.5, t0 + 7, grp + ["stitch"])                      # 针迹也留实的（不然透视时看不见已缝的花样）
    _bad_labels(lab, c, t0, t0 + 7)
    run(7, slow_span)
    st.append(round(t0 + 3.5, 2))
