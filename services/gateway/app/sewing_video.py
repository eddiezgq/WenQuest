"""缝纫机设计软件：按这台设计一键出三维讲解片（第 56 轮）。

不用写一句话：按当前这组参数自动写好场景（tools/blender/场景格式.md 的格式，模型 gen:sewdesign = 设计软件自己的零件），
交给平台的“三维视频”服务（第 38 轮 video3d.py）：关键画面在自己服务器上出，小样、高清租云端 GPU，片子进本人的三维视频列表，
之后也能像别的三维视频一样提意见让 AI 改镜头和节奏。
- 段落：整机 → 各机构（平缝机：刺布、挑线、钩线、送布；包缝机：引针、下弯针、上弯针、送布与差动、切刀）→ 红黄灯项（最多 3 项，
  在出问题的机构上慢放、透视，写出数值和判据）→ 整机和结论。
- 数全由计算核心给（analyze 的校核值和参数），AI 不写数；以后 AI 改场景时，设计参数锁定（video3d.Service 的 lock）。
- 谁能用：缝纫机设计软件已开通的单位（同 CAE），以及能用三维视频的老师。收费：第 56 轮只记账（video3d 的 runs 表）。

  POST /api/v1/sewing/video   {machine, params} → {id}（三维视频的 id；网页跳到三维视频页看关键画面、出小样和高清）
"""

import math
from typing import Annotated, Any

import yaml
from fastapi import Depends
from pydantic import BaseModel, Field

from . import sewcore
from .moodle import EngineError
from . import video3d as v3
from .sewcore import cad

MACHINES = ("lockstitch", "overlock")
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
# 校核项 → 出问题的机构（组）、慢放到哪个主轴转角附近（None = 整圈）
LOCK_PROBLEM = {"needle_force": ("needle", 180), "lambda": ("needle", None), "catch_rise": ("hook", "catch"), "hook": ("hook", "catch"),
                "chain": ("hook", "catch"), "frame_force": ("all", None), "frame_res": ("all", None)}
OL_PROBLEM = {"feed_window": "feed", "lambda": "needle", "diff": "feed", "diff_range": "feed", "knife_time": "knife", "knife_ov": "knife"}


def _section_groups(machine: str) -> list:
    return LOCK_SECTIONS if machine == "lockstitch" else OL_SECTIONS


def _names_in(machine: str, params: dict, groups: list[str]) -> list[str]:
    """组名可以是机构名（needle……）也可以是零件名；返回零件名清单"""
    G = cad.GROUPS
    names = [p["name"] for p in cad.parts3d(params, 0.0, machine)["parts"]]
    out = []
    for n in names:
        if n in groups or G.get(n, "frame") in groups:
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
        }
    return {k: (_join(zh, 46), _join(en, 110)) for k, (zh, en) in rows.items()}


def problem_target(machine: str, key: str, catch: float) -> tuple[list[str], float | None]:
    """红黄灯项 → 要透视的组、慢放的转角"""
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
    cap = captions(machine, R)
    catch = None
    if machine == "lockstitch":
        mech = sewcore.design.mech_of(p)
        catch = round(mech.PHC0 + p["psi"] / 2, 1)
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
    labels.append({"t": [0, 6], "zh": _short(f"这台{name_zh}：{p['n']:g} r/min，零件尺寸按你的设计", 46),
                   "en": _short(f"This {name_en.lower()} machine: {p['n']:g} r/min, parts at your design dimensions", 120)})
    labels.append({"t": [0, 6], "where": "bottom", "zh": "机构零件、尺寸和运动都由设计软件的计算核心给出",
                   "en": "Parts, dimensions and motion come from the design software's computation core"})
    st_whole.append(3.0)
    run(6, 720)
    # 2 各机构：一段一圈慢放、透视这个机构
    for key, groups, (tz, te) in _section_groups(machine):
        names = _names_in(machine, p, groups)
        if not names:
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
        groups, phi = problem_target(machine, c["key"], catch)
        names = _names_in(machine, p, groups)
        cc, dg = _extent(machine, p, names or None)
        dist = round(max(0.18, 3.4 * dg), 3)
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
    labels.append({"t": [round(t0, 2), round(t0 + 6, 2)], "where": "bottom", "zh": "问渠缝纫机设计软件 · 计算书、STEP、调机卡同一组参数",
                   "en": "WenQuest sewing design software · same parameters as report, STEP, setup card"})
    run(6, 720)
    dur = round(t, 2)
    stills = st_whole + st_prob
    stills += st_sec[: max(0, 6 - len(stills) - 1)] + [round(t0 + 3.0, 2)]          # 余下的给各机构，最后一张是结论
    spec: dict[str, Any] = {
        "name": f"{name_zh}讲解",
        "title": {"zh": _short(f"{name_zh}的机构怎么动", 40), "en": _short(f"How this {name_en.lower()} machine works", 100)},
        "duration": dur, "floor": False, "clip": 0.002,
        "models": [{"id": "d", "use": "gen:sewdesign", "machine": machine, "params": {k: v for k, v in p.items() if not isinstance(v, (list, dict))}}],
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
    else:
        spec["panel"] = {"kind": "readouts", "head": "读数  Readouts", "items": [{"zh": "主轴转角", "en": "shaft", "key": "phi", "fmt": "{:5.0f}", "unit": "°"}]}
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
            mk["zh"] = {"最低点": "BDC", "钩线": "catch"}.get(mk["zh"], mk["zh"]) if lang == "en" else mk["zh"]
    text = ("# 缝纫机设计软件按这台设计自动写的讲解片场景（第 56 轮）。数由计算核心给，模型参数锁定。\n"
            + yaml.dump(spec, Dumper=_Plain, allow_unicode=True, sort_keys=False, width=200))
    return text, {"duration": dur, "bad": nb, "warn": nw, "problems": [c["key"] for c in bad[:3]], "title": spec["title"],
                  "numbers": sorted(v3.label_numbers(spec))}


class _Plain(yaml.SafeDumper):
    """不写 &id001 这类引用：人和 AI 改场景时一眼看得懂"""
    def ignore_aliases(self, data):
        return True


class VideoIn(BaseModel):
    machine: str = Field(default="lockstitch", pattern="^(lockstitch|overlock)$")
    params: dict[str, Any] = Field(default_factory=dict)
    project: str = Field(default="", max_length=80)
    lang: str = Field(default="zh", pattern="^(zh|en|both)$")


def register(app, m) -> None:
    from . import video3d_api

    @app.post("/api/v1/sewing/video")
    async def make_video(body: VideoIn, sess: Annotated[Any, Depends(m.current)]):
        lic = await m.sewing_need_license(sess)
        svc = video3d_api.service(m)
        text, meta = scene(body.machine, body.params, body.lang)
        V = await svc.create(sess.user_id, lic.get("org") or "", "", "")
        p = sewcore.get(body.machine).clean(body.params)
        V["lock"] = {"model": "d", "machine": body.machine, "params": {k: v for k, v in p.items() if not isinstance(v, (list, dict))},
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
                                  + (f"，再把 {len(meta['problems'])} 项红黄灯慢放标出" if probs else "") + "）。正在出关键画面；"
                                  "看过可以直接出小样、高清，或者告诉我要改什么（镜头、节奏、字幕都能改，设计参数和数值不改）。"})
        svc.store.save(V)
        if svc.blender.on:
            V["stills"] = {"state": "running", "version": V.get("version")}
            svc.store.save(V)
            svc.spawn(svc.stills(V["id"]))
        return {"id": V["id"], "duration": meta["duration"], "problems": meta["problems"]}
