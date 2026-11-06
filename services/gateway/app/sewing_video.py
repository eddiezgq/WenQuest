"""缝纫机设计软件：按这台设计一键出三维讲解片（第 56 轮）。

不用写一句话：按当前这组参数自动写好场景（tools/blender/场景格式.md 的格式，模型 gen:sewdesign = 设计软件自己的零件），
交给平台的“三维视频”服务（第 38 轮 video3d.py）：关键画面在自己服务器上出，小样、高清租云端 GPU，片子进本人的三维视频列表，
之后也能像别的三维视频一样提意见让 AI 改镜头和节奏。
- 段落：整机 → 各机构（平缝机：刺布、挑线、钩线、送布；包缝机：引针、下弯针、上弯针、送布与差动、切刀；
  绷缝机（第 76 轮）：引线、弯针、钩线（在钩线角慢放，弯针依次钩各针的线环）、撑线器（602、605）、送布）→ 红黄灯项（最多 3 项，
  在出问题的机构上慢放、透视，写出数值和判据）→ 整机和结论。
- 花样机、刺绣机、横机（第 89 轮）按针 / 按趟走，场景由 sewing_video_seq.py 写：一针（一趟）慢放 → 移动 → 快放走完，
  途中在最紧的一针和出问题的那一针 / 那一趟停下慢放 → 结论。
- 数全由计算核心给（analyze 的校核值和参数），AI 不写数；以后 AI 改场景时，设计参数锁定（video3d.Service 的 lock）。
- 谁能用：缝纫机设计软件已开通的单位（同 CAE），以及能用三维视频的老师。收费：第 56 轮只记账（video3d 的 runs 表）。

  POST /api/v1/sewing/video   {machine, params} → {id}（三维视频的 id；网页跳到三维视频页看关键画面、出小样和高清）
"""

import math
import re
from typing import Annotated, Any

import yaml
from fastapi import Depends
from pydantic import BaseModel, Field

from . import sewcore
from .moodle import EngineError
from . import video3d as v3
from .sewcore import cad
from . import sewing_video_seq as SEQ

MACHINES = ("lockstitch", "overlock", "cover", "pattern", "embroid", "flatknit")      # 后三种第 89 轮，场景见 sewing_video_seq.py
S = 0.001                      # 毫米 → 米（渲染器的单位）

# 平板、轴、球……按零件名分到机构（与 tools/blender/sewdesign.py 的 GROUP 一致）
LOCK_SECTIONS = [
    ("needle", ["needle"], ("① 刺布机构（曲柄滑块）", "① Needle bar (slider-crank)")),
    ("takeup", ["takeup"], ("② 挑线机构（四杆）", "② Take-up (four-bar)")),
    ("hook", ["hook"], ("③ 钩线：旋梭（转速是主轴的 2 倍）", "③ Hook: rotary hook at twice shaft speed")),
    ("feed", ["feed", "frame"], ("④ 送布：抬牙和送布偏心轮带送布牙", "④ Feed: lift and feed eccentrics drive the feed dog")),
]
OL_SECTIONS = [
    ("needle", ["needle"], ("① 斜向引针（曲柄滑块）", "① Slanted needle drive (slider-crank)")),
    ("lower", ["LL_Eccentric", "LL_BallA", "LL_BallB", "LL_Link", "LL_Rocker", "LL_Shaft", "LL_Looper"],
     ("② 下弯针：空间四杆（RSSR）", "② Lower looper: spatial four-bar (RSSR)")),
    ("upper", ["UL_Eccentric", "UL_BallA", "UL_BallB", "UL_Link", "UL_Rocker", "UL_Shaft"],
     ("③ 上弯针：空间四杆（RSSR）", "③ Upper looper: spatial four-bar (RSSR)")),
    ("feed", ["feed"], ("④ 送布与差动：主送布臂、差动送布臂", "④ Feed and differential: main and differential arms")),
    ("knife", ["knife"], ("⑤ 切边：上刀、下刀", "⑤ Edge trimming: upper and lower knives")),
]
# 绷缝机（第 76 轮）：第 4 项是这一段慢放到哪个转角（"catch" = 钩线角附近，弯针从右往左依次钩各针）、透视哪些组
CV_SECTIONS = [
    ("needle", ["needle"], ("① 引线：针杆曲柄滑块带一排机针", "① Needle drive: slider-crank with the row of needles"), None),
    ("looper", ["looper"], ("② 弯针：左右摆 + 前后避针，刀尖走扁椭圆", "② Looper: swing across + needle avoidance, a flat ellipse"), None),
    ("catch", ["needle", "looper", "thread"], ("③ 钩线：弯针从右往左依次钩住各针的线环", "③ Catching: the looper takes each needle loop, right to left"),
     "catch"),
    ("spreader", ["spreader"], ("④ 撑线器：把覆盖线铺过各针", "④ Spreader: lays the cover thread across the needles"), None),
    ("feed", ["feed", "frame"], ("⑤ 送布：主送布牙、差动送布牙", "⑤ Feed: main and differential feed dogs"), None),
]
CV_PROBLEM = {"loop_rise": "catch", "point_h": "catch", "gap": "catch", "timing_margin": "catch", "descend": "fd", "avoid": "fd"}
# 校核项 → 出问题的机构（组）、慢放到哪个主轴转角附近（None = 整圈）
LOCK_PROBLEM = {"needle_force": ("needle", 180), "lambda": ("needle", None), "catch_rise": ("hook", "catch"), "hook": ("hook", "catch"),
                "chain": ("hook", "catch"), "frame_force": ("all", None), "frame_res": ("all", None)}
OL_PROBLEM = {"feed_window": "feed", "lambda": "needle", "diff": "feed", "diff_range": "feed", "knife_time": "knife", "knife_ov": "knife"}


def _section_groups(machine: str) -> list:
    """(键, 组, 标题, 慢放的转角) —— 平缝、包缝每段整圈"""
    if machine == "cover":
        return CV_SECTIONS
    return [s + (None,) for s in (LOCK_SECTIONS if machine == "lockstitch" else OL_SECTIONS)]


def _names_in(machine: str, params: dict, groups: list[str]) -> list[str]:
    """组名可以是机构名（needle……）也可以是零件名；返回零件名清单"""
    names = [p["name"] for p in cad.parts3d(params, 0.0, machine)["parts"]]
    out = []
    for n in names:
        if n in groups or cad.group_of(n) in groups:
            out.append(n)
    return out



def _extent(machine: str, params: dict, names: list[str] | None) -> tuple[list[float], float]:
    """这些零件在一圈里扫过的范围：中心（米）和对角线长（米），给镜头用"""
    lo, hi = [1e9] * 3, [-1e9] * 3
    for a in range(0, 360, 30):
        for p in cad.parts3d(params, float(a), machine)["parts"]:
            if names is not None and p["name"] not in names:
                continue
            pts = []
            if "base" in p:
                pts.append(p["base"])
                if p["type"] == "cyl":
                    pts.append([p["base"][i] + p["dir"][i] * p["h"] for i in range(3)])
                if p["type"] == "box":
                    pts.append([p["base"][i] + p["size"][i] for i in range(3)])
            if "c" in p:
                pts.append(p["c"])
            if p["type"] == "tube":
                pts += p["pts"]
            if p["type"] == "plate":
                f = p.get("frame")
                for x, z, rc in p["circles"]:          # 平板的轮廓是几个圆的凸包：圆心 ± 半径
                    for dx, dz in ((rc, 0), (-rc, 0), (0, rc), (0, -rc)):
                        if f:
                            pts.append([f["o"][i] + (x + dx) * f["u"][i] + (z + dz) * f["v"][i] for i in range(3)])
                        else:
                            pts.append([x + dx, p["y0"], z + dz])
            r = p.get("r", 0) if p["type"] in ("cyl", "sphere") else 0          # 短粗圆柱：半径才是大小
            for q in pts:
                for i in range(3):
                    lo[i], hi[i] = min(lo[i], q[i] - r), max(hi[i], q[i] + r)
    diag = math.dist(lo, hi) * S
    # 镜头对准点往下挪一点：零件在画面里偏上，不被下方的字幕条挡住
    c = [(lo[0] + hi[0]) / 2 * S, (lo[1] + hi[1]) / 2 * S, (lo[2] + hi[2]) / 2 * S - 0.06 * diag]
    return [round(x, 4) for x in c], diag


def _cover_close(params: dict) -> tuple[list[float], float]:
    """绷缝机成缝区特写：对着弯针平面上的一排针（线环只有一两毫米，要拉得很近）"""
    m = cad.parts3d(params, 0.0, "cover")
    xs = [q["base"][0] for q in m["parts"] if re.fullmatch(r"CV_Needle\d", q["name"])]
    c = [round((min(xs) + max(xs)) / 2 * S, 4), 0.0, round((m["zb"] - 0.5) * S, 4)]
    return c, round(0.028 + 0.9 * (max(xs) - min(xs)) * S, 3)


def _short(s: str, n: int) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def _check(R: dict, key: str) -> dict | None:
    return next((c for c in R["checks"] if c["key"] == key), None)


def _val(R: dict, key: str, lang: str = "zh") -> str:
    c = _check(R, key)
    return c["value"][lang] if c else ""


def _join(parts: list[str], n: int) -> str:
    """几项用“ · ”连起来，放不下的整项不要（不把数截断）"""
    out = ""
    for x in parts:
        y = x if not out else out + " · " + x
        if len(y) > n:
            break
        out = y
    return out or _short(parts[0], n)


def captions(machine: str, R: dict) -> dict[str, tuple[str, str]]:
    """各段底部字幕：这台设计自己的数（全由 analyze 给）。重要的数放前面，放不下的整项不要（不把数截断）。"""
    p = R["params"]
    v = lambda k, lang="zh": _val(R, k, lang)  # noqa: E731
    if machine == "lockstitch":
        rows = {
            "needle": ([f"下止点惯性力 {v('needle_force')}", f"连杆比 {v('lambda')}", f"曲柄 {p['r']:g} mm", f"连杆 {p['l']:g} mm"],
                       [f"Inertia force at BDC {v('needle_force', 'en')}", f"rod ratio {v('lambda', 'en')}", f"crank {p['r']:g} mm", f"rod {p['l']:g} mm"]),
            "takeup": ([f"挑线余量（最小）{v('takeup_margin')}", f"传动角 {v('takeup_mu')}"],
                       [f"Take-up margin (min.) {v('takeup_margin', 'en')}", f"transmission angle {v('takeup_mu', 'en')}"]),
            "hook": ([f"钩线时机针回升 {v('catch_rise')}", f"旋梭定时 {p['psi']:g}°"],
                     [f"Needle rise at pickup {v('catch_rise', 'en')}", f"hook timing {p['psi']:g}°"]),
            "feed": ([f"实际针距 {v('feed_slip').split('（')[0]}", f"针距 {p['s']:g} mm", f"送布牙高出针板 {p['h']:g} mm"],
                     [f"Actual / set stitch {v('feed_slip', 'en').split(' (')[0]}", f"stitch {p['s']:g} mm", f"feed dog {p['h']:g} mm above the plate"]),
        }
    else:
        rows = {
            "needle": ([f"连杆比 {v('lambda')}", f"转速 {p['n']:g} r/min"], [f"Rod ratio {v('lambda', 'en')}", f"{p['n']:g} r/min"]),
            "lower": ([f"摆角与弧长 {v('ll_swing')}", f"最小传动角 {v('ll_gamma')}"],
                      [f"Swing {v('ll_swing', 'en')}", f"min. transmission angle {v('ll_gamma', 'en')}"]),
            "upper": ([f"上弯针最小传动角 {v('ul_gamma')}"], [f"Upper looper min. transmission angle {v('ul_gamma', 'en')}"]),
            "feed": ([f"布边 {v('diff')}", f"差动比 {p['D']:g}"], [f"Edge {v('diff', 'en')}", f"differential ratio {p['D']:g}"]),
            "knife": ([f"上下刀重叠 {v('knife_ov')}"], [f"Knife overlap {v('knife_ov', 'en')}"]),
        } if machine == "overlock" else {
            "needle": ([f"线迹 {p['stitch']}", f"{_n_needles(p)} 根针，针距 {p['g']:g} mm", f"{p['n']:g} r/min"],
                       [f"Stitch {p['stitch']}", f"{_n_needles(p)} needle(s), gauge {p['g']:g} mm", f"{p['n']:g} r/min"]),
            "looper": ([f"弯针定时 {p['dphi']:+g}°", _win(v("timing_margin"), "zh"), f"回退量 {p['rr']:g} mm", f"让针幅度 {p['e']:g} mm"],
                       [f"Looper timing {p['dphi']:+g}°", _win(v("timing_margin", "en"), "en"), f"retraction {p['rr']:g} mm",
                        f"avoid amplitude {p['e']:g} mm"]),
            "catch": ([f"钩线时机针回升 {v('loop_rise')}", f"弯针尖高出针眼 {v('point_h')}", f"间隙 {v('gap')}"],
                      [f"Needle rise at the catch {v('loop_rise', 'en')}", f"point above the eye {v('point_h', 'en')}", f"clearance {v('gap', 'en')}"]),
            "spreader": (["钩尖在布面上方左右摆，把覆盖线横拉过各针（10.5 节）"],
                         ["The hook swings above the fabric, drawing the cover thread across the needles (Section 10.5)"]),
            "feed": ([f"针密 {p['spc']:g} /cm", "主、差动两只送布牙"], [f"{p['spc']:g} stitches/cm", "main and differential dogs"]),
        }
    return {k: (_join(zh, 46), _join(en, 110)) for k, (zh, en) in rows.items()}


def _win(val: str, lang: str) -> str:
    """“弯针定时离窗口边缘”的值里取窗口那一半；没有窗口时照原话"""
    if lang == "zh":
        return "可行" + val.split("，")[-1] if "窗口" in val else val
    return "workable " + val.split(", ", 1)[-1] if "window" in val else val


def _n_needles(p: dict) -> int:
    return sewcore.get("cover").TY[p["stitch"]][0]


def _avoid_angle(M, p: dict) -> float | None:
    """“针在弯针平面下方时不相碰”不合格时，间隙最小的转角（后侧在针回升时、前侧在针下行时；同 cover.evaluate 的扫法）"""
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
        return OL_SECTIONS[1][1], None
    if key.startswith("ul_"):
        return OL_SECTIONS[2][1], None
    return [OL_PROBLEM.get(key, "needle")], None


def scene(machine: str, params: dict | None, lang: str = "both") -> tuple[str, dict]:
    """自动写场景（YAML 文本）和摘要。lang：both 中英两行；zh / en 只出一种（跟设计软件的“文件语言”走）。"""
    if machine not in MACHINES:
        raise ValueError(machine)
    M = sewcore.get(machine)
    p = M.clean(params or {})
    R = M.analyze(p, trial=False) if machine == "lockstitch" else M.analyze(p)
    name_zh, name_en = M.NAME
    if machine in SEQ.MACHINES:                 # 第 89 轮：花样机、刺绣机、横机按针 / 按趟走
        spec, info = SEQ.scene_seq(machine, p, R, name_zh, name_en)
        return _finish(spec, lang, info["bad"], info["warn"], info["problems"])
    cap = captions(machine, R)
    catch = fd = None
    if machine == "lockstitch":
        mech = sewcore.design.mech_of(p)
        catch = round(mech.PHC0 + p["psi"] / 2, 1)
    if machine == "cover":
        E = M.evaluate({k: p[k] for k in ("dphi", "dz", "e", "gap", "rr")})
        catch, fd = round(E["fc"], 1), round(E["fd"], 1)
        # 左边的针：弯针尖从右往左走到这根针的转角（钩线去程，同模型 10-1 的 layout）
        n_n, g = _n_needles(p), p["g"]
        xs = [0.0] if n_n == 1 else [-g, 0.0] if n_n == 2 else [-g, -g / 2, 0.0]
        phR = M.PHR0 + p["dphi"]
        last = max(M.bis(lambda f, dx=dx: E["looper"](f)[0] - dx, phR, phR + 180) for dx in xs) if min(xs) < 0 else E["fc"]
    whole_c, whole_d = _extent(machine, p, None)
    dist_whole = round(max(0.25, 2.8 * whole_d), 3)
    t, angle, cams, labels, effects = 0.0, [[0, 0]], [], [], []
    st_whole, st_sec, st_prob = [], [], []          # 关键画面：整机、各机构中段、红黄灯停在出问题的转角
    a = 0.0

    def run(dt: float, deg: float):
        nonlocal t, a
        t += dt
        a += deg
        angle.append([round(t, 2), round(a, 1)])

    # 1 整机
    cams += [{"t": 0, "look": whole_c, "az": -40, "el": 18, "dist": dist_whole, "lens": 40},
             {"t": 5.5, "look": whole_c, "az": -20, "el": 14, "dist": round(dist_whole * 0.92, 3), "lens": 40}]
    if machine == "cover":              # 绷缝机的机构尺寸是示意（教材模型 10-1），运动、线环和判据按这台设计
        labels.append({"t": [0, 6], "zh": _short(f"这台{name_zh}：{p['stitch']} 线迹，{p['n']:g} r/min", 46),
                       "en": _short(f"This {name_en.lower()} machine: stitch {p['stitch']}, {p['n']:g} r/min", 120)})
        labels.append({"t": [0, 6], "where": "bottom", "zh": "针、弯针的运动和线环按你的设计算；机构尺寸为示意",
                       "en": "Needle and looper motion and the loops follow your design; mechanism sizes are illustrative"})
    else:
        labels.append({"t": [0, 6], "zh": _short(f"这台{name_zh}：{p['n']:g} r/min，零件尺寸按你的设计", 46),
                       "en": _short(f"This {name_en.lower()} machine: {p['n']:g} r/min, parts at your design dimensions", 120)})
        labels.append({"t": [0, 6], "where": "bottom", "zh": "机构零件、尺寸和运动都由设计软件的计算核心给出",
                       "en": "Parts, dimensions and motion come from the design software's computation core"})
    st_whole.append(3.0)
    run(6, 720)
    # 2 各机构：一段一圈慢放、透视这个机构
    k_no = 0
    for key, groups, (tz, te), slow in _section_groups(machine):
        names = _names_in(machine, p, groups)
        if not names:
            continue
        k_no += 1                               # 段号按出现的段重排（406 没有撑线器那段，送布是④）
        tz, te = "①②③④⑤⑥"[k_no - 1] + tz[1:], "①②③④⑤⑥"[k_no - 1] + te[1:]
        if slow == "catch":                     # 钩线：先转到钩线角前 30°，再用 7 秒走过各针的钩线角，看得清线环
            c, dist = _cover_close(p)
            t0 = t
            cams += [{"t": round(t0 + 0.8, 2), "look": c, "az": -55, "el": 8, "dist": dist, "lens": 40},
                     {"t": round(t0 + 8.0, 2), "look": c, "az": -35, "el": 6, "dist": dist, "lens": 40}]
            effects.append({"kind": "xray", "t": [round(t0 + 0.5, 2), round(t0 + 8.5, 2)], "top": [f"d.{g}" for g in groups]})
            labels.append({"t": [round(t0, 2), round(t0 + 9, 2)], "zh": _short(tz, 46), "en": _short(te, 120)})
            if key in cap:
                labels.append({"t": [round(t0, 2), round(t0 + 9, 2)], "where": "bottom", "zh": _short(cap[key][0], 46),
                               "en": _short(cap[key][1], 120)})
            span = (last - catch) % 360 + 40
            target = (math.floor(a / 360) + 1) * 360 + catch - 30
            run(1, target - a)
            run(7, span)
            run(1, 0)
            st_sec.append(round(t0 + 1 + 7 * 30 / span, 2))          # 正好在钩线角
            continue
        c, dg = _extent(machine, p, names)
        dist = round(max(0.18, 3.4 * dg), 3)
        t0 = t
        cams += [{"t": round(t0 + 1.0, 2), "look": c, "az": -35, "el": 12, "dist": dist, "lens": 40},
                 {"t": round(t0 + 7.0, 2), "look": c, "az": -20, "el": 10, "dist": dist, "lens": 40}]
        effects.append({"kind": "xray", "t": [round(t0 + 0.5, 2), round(t0 + 7.5, 2)], "top": [f"d.{g}" for g in groups]})
        labels.append({"t": [round(t0, 2), round(t0 + 8, 2)], "zh": _short(tz, 46), "en": _short(te, 120)})
        if key in cap:
            labels.append({"t": [round(t0, 2), round(t0 + 8, 2)], "where": "bottom", "zh": _short(cap[key][0], 46), "en": _short(cap[key][1], 120)})
        st_sec.append(round(t0 + 4.0, 2))
        run(8, 360)
    # 3 红黄灯：先红后黄，最多 3 项
    bad = [c for c in R["checks"] if c["state"] == "bad"] + [c for c in R["checks"] if c["state"] == "warn"]
    for c in bad[:3]:
        groups, phi = problem_target(machine, c["key"], catch, fd, _avoid_angle(M, p) if machine == "cover" else None)
        names = _names_in(machine, p, groups)
        cc, dg = _extent(machine, p, names or None)
        dist = round(max(0.18, 3.4 * dg), 3)
        if machine == "cover" and phi is not None:          # 绷缝机出在成缝区：镜头拉到针尖、弯针尖一带
            cc, dist = _cover_close(p)
        t0 = t
        tag = ("不合格", "fails") if c["state"] == "bad" else ("注意", "check")
        cams += [{"t": round(t0 + 1.0, 2), "look": cc, "az": -50, "el": 15, "dist": dist, "lens": 40},
                 {"t": round(t0 + 6.0, 2), "look": cc, "az": -30, "el": 12, "dist": dist, "lens": 40}]
        effects.append({"kind": "xray", "t": [round(t0 + 0.5, 2), round(t0 + 6.5, 2)], "top": [f"d.{g}" for g in groups]})
        labels.append({"t": [round(t0, 2), round(t0 + 7, 2)], "tone": c["state"], "zh": _short(f"⚠ {tag[0]}：{c['name']['zh']}", 46),
                       "en": _short(f"⚠ {c['name']['en']} {tag[1]}", 120)})
        labels.append({"t": [round(t0, 2), round(t0 + 7, 2)], "where": "bottom",
                       "zh": _join([c["value"]["zh"], f"判据 {c['limit']['zh']}"], 46),
                       "en": _join([c["value"]["en"], f"criterion {c['limit']['en']}"], 110)})
        if phi is not None:              # 停在出问题的转角附近慢放：先转到 phi − 40°，再用 5 秒走 80°
            target = (math.floor(a / 360) + 1) * 360 + phi - 40
            run(1, target - a)
            run(5, 80)
            run(1, 0)
            st_prob.append(round(t0 + 3.5, 2))              # 走到 phi 正好在 5 秒慢放的中间
        else:
            st_prob.append(round(t0 + 3.5, 2))
            run(7, 360)
    # 4 结论
    t0 = t
    nb = sum(c["state"] == "bad" for c in R["checks"])
    nw = sum(c["state"] == "warn" for c in R["checks"])
    concl = ((f"全部 {len(R['checks'])} 项校核合格", f"All {len(R['checks'])} checks pass") if not nb and not nw else
             (f"{len(R['checks'])} 项校核：不合格 {nb} 项，注意 {nw} 项", f"{len(R['checks'])} checks: {nb} fail, {nw} need attention"))
    cams += [{"t": round(t0 + 1.5, 2), "look": whole_c, "az": -30, "el": 18, "dist": dist_whole, "lens": 40},
             {"t": round(t0 + 6, 2), "look": whole_c, "az": -45, "el": 20, "dist": dist_whole, "lens": 40}]
    labels.append({"t": [round(t0, 2), round(t0 + 6, 2)], "zh": _short(concl[0], 46), "en": _short(concl[1], 120)})
    labels.append({"t": [round(t0, 2), round(t0 + 6, 2)], "where": "bottom",
                   "zh": "问渠缝纫机设计软件 · 计算书、调机卡同一组参数" if machine == "cover" else "问渠缝纫机设计软件 · 计算书、STEP、调机卡同一组参数",
                   "en": "WenQuest sewing design software · same parameters as report, setup card" if machine == "cover"
                   else "WenQuest sewing design software · same parameters as report, STEP, setup card"})
    run(6, 720)
    dur = round(t, 2)
    stills = st_whole + st_prob
    stills += st_sec[: max(0, 6 - len(stills) - 1)] + [round(t0 + 3.0, 2)]          # 余下的给各机构，最后一张是结论
    spec: dict[str, Any] = {
        "name": f"{name_zh}讲解",
        "title": {"zh": _short(f"{name_zh}的机构怎么动", 40), "en": _short(f"How this {name_en.lower()} machine works", 100)},
        "duration": dur, "floor": False, "clip": 0.002,
        "models": [{"id": "d", "use": "gen:sewdesign", "machine": machine, "params": SEQ.spec_params(p)}],
        "motion": [{"drive": "weblab", "model": "d", "angle": angle}],
        "camera": cams, "effects": effects, "labels": labels, "stills": sorted(stills)[:6],
    }
    if machine == "lockstitch":
        spec["panel"] = {"kind": "readouts", "head": "读数  Readouts", "items": [
            {"zh": "主轴转角", "en": "shaft", "key": "phi", "fmt": "{:5.0f}", "unit": "°"},
            {"zh": "针尖高出针板", "en": "needle tip", "key": "needle", "fmt": "{:+6.1f}", "unit": " mm", "scale": 25},
            {"zh": "旋梭转角", "en": "hook", "key": "hookdeg", "fmt": "{:5.0f}", "unit": "°"}],
            "plot": {"key": "needle", "zh": "针尖高度", "en": "needle height",
                     "marks": [{"phi": 180, "zh": "最低点"}, {"phi": round(catch) % 360, "zh": "钩线"}]}}
    elif machine == "cover":
        spec["panel"] = {"kind": "readouts", "head": "读数  Readouts", "items": [
            {"zh": "主轴转角", "en": "shaft", "key": "phi", "fmt": "{:5.0f}", "unit": "°"},
            {"zh": "针尖高出弯针平面", "en": "needle above looper", "key": "needle", "fmt": "{:+6.1f}", "unit": " mm", "scale": 25},
            {"zh": "弯针尖左右位置", "en": "looper point", "key": "looper", "fmt": "{:+6.1f}", "unit": " mm"}],
            "plot": {"key": "needle", "zh": "针尖高度", "en": "needle height",
                     "marks": [{"phi": round(catch) % 360, "zh": "钩线"}, {"phi": round(fd) % 360, "zh": "针到弯针平面"}]}}
    else:
        spec["panel"] = {"kind": "readouts", "head": "读数  Readouts", "items": [{"zh": "主轴转角", "en": "shaft", "key": "phi", "fmt": "{:5.0f}", "unit": "°"}]}
    return _finish(spec, lang, nb, nw, [c["key"] for c in bad[:3]])


FOOT_EN = {"（横轴：针号）": " (x: stitch no.)", "（横轴：趟）": " (x: pass)"}
MARK_EN = {"最低点": "BDC", "钩线": "catch", "针到弯针平面": "needle at looper", "最紧": "tightest", "最难": "hardest", "最宽": "widest"}


def _finish(spec: dict, lang: str, nb: int, nw: int, problems: list[str]) -> tuple[str, dict]:
    """按文件语言收面板的中英文，写成 YAML；摘要"""
    if lang in ("zh", "en"):
        spec["lang"] = lang
        pan = spec["panel"]
        pan["head"] = "读数" if lang == "zh" else "Readouts"
        for it in pan["items"] + ([pan["plot"]] if "plot" in pan else []):
            if lang == "zh":
                it["en"] = ""
            else:
                it["zh"], it["en"] = it["en"], ""
        for mk in pan.get("plot", {}).get("marks", []):
            mk["zh"] = MARK_EN.get(mk["zh"], mk["zh"]) if lang == "en" else mk["zh"]
        if "foot" in pan.get("plot", {}) and lang == "en":
            pan["plot"]["foot"] = FOOT_EN.get(pan["plot"]["foot"], pan["plot"]["foot"])
    elif "foot" in spec["panel"].get("plot", {}):
        pl = spec["panel"]["plot"]
        pl["foot"] = pl["foot"] + FOOT_EN.get(pl["foot"], "")
    text = ("# 缝纫机设计软件按这台设计自动写的讲解片场景（第 56 轮）。数由计算核心给，模型参数锁定。\n"
            + yaml.dump(spec, Dumper=_Plain, allow_unicode=True, sort_keys=False, width=200))
    return text, {"duration": spec["duration"], "bad": nb, "warn": nw, "problems": problems, "title": spec["title"],
                  "params": spec["models"][0]["params"],
                  "numbers": sorted(v3.label_numbers(spec))}


class _Plain(yaml.SafeDumper):
    """不写 &id001 这类引用：人和 AI 改场景时一眼看得懂"""
    def ignore_aliases(self, data):
        return True


class VideoIn(BaseModel):
    machine: str = Field(default="lockstitch", pattern="^(lockstitch|overlock|cover|pattern|embroid|flatknit)$")
    params: dict[str, Any] = Field(default_factory=dict)
    project: str = Field(default="", max_length=80)
    lang: str = Field(default="zh", pattern="^(zh|en|both)$")
    voice: bool = True                  # 第 90 轮：配旁白（念画面上的字，旁白长的段放慢拉长）


def register(app, m) -> None:
    from . import video3d_api

    @app.post("/api/v1/sewing/video")
    async def make_video(body: VideoIn, sess: Annotated[Any, Depends(m.current)]):
        lic = await m.sewing_need_license(sess)
        svc = video3d_api.service(m)
        text, meta = scene(body.machine, body.params, body.lang)
        V = await svc.create(sess.user_id, lic.get("org") or "", "", "")
        V["lock"] = {"model": "d", "machine": body.machine, "params": meta["params"],
                     "numbers": meta["numbers"]}
        V["sewing"] = {"machine": body.machine, "project": body.project, "org": lic.get("org") or ""}
        svc.store.save(V)
        errs = svc.set_scene(V, text)
        if errs:              # 不该发生（自动写的场景都过检查）；万一发生，不留下打不开的空片子
            svc.store.delete(V["id"])
            raise EngineError("bad_scene", "；".join(errs[:3]), 500)
        V = svc.store.load(V["id"])
        t = meta["title"]
        V["title"] = {"zh": _short((body.project + " · " if body.project else "") + t["zh"], 60), "en": _short(t["en"], 120)}
        probs = "；".join(meta["problems"]) if meta["problems"] else ""
        V["chat"].append({"who": "ai", "at": video3d_api.v3.now(),
                          "text": f"按这台设计自动写好了场景（{meta['duration']:g} 秒：整机、各机构"
                                  + (f"，再把 {len(meta['problems'])} 项红黄灯慢放标出" if probs else "") + "）。"
                                  + ("正在配旁白，配好接着出关键画面；" if body.voice else "正在出关键画面；") +
                                  "看过可以直接出小样、高清，或者告诉我要改什么（镜头、节奏、字幕都能改，设计参数和数值不改）。"})
        if body.voice:
            V["voice"], V["busy"] = {"on": True, "state": "running"}, "voice"
        svc.store.save(V)
        if body.voice:
            svc.spawn(svc.revoice(V["id"]))                 # 配完接着出关键画面（拉长以后关键画面的时刻变了）
        elif svc.blender.on:
            V["stills"] = {"state": "running", "version": V.get("version")}
            svc.store.save(V)
            svc.spawn(svc.stills(V["id"]))
        return {"id": V["id"], "duration": meta["duration"], "problems": meta["problems"], "voice": body.voice}
