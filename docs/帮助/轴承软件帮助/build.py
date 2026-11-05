# -*- coding: utf-8 -*-
"""问渠轴承的网页互动帮助（第 90 轮）：一份源文件，生成两份帮助。

  python3 docs/帮助/轴承软件帮助/build.py          （要 pip install markdown；计算核心在 services/bearing）

生成（放在轴承网页版自己的静态目录里，和软件、计算接口同一个网址，国内版、美国版都一样）：
  apps/bearing/public/help/index.html                    网页版帮助（…/bearing/help/）
  apps/bearing/public/help/freecad/index.html            FreeCAD 版帮助的在线一份（…/bearing/help/freecad/）
  apps/bearing/public/help/media/…                       视频、封面、字幕（tools/ 里的录屏程序生成）
  services/bearing/freecad/help/…                        FreeCAD 版帮助的离线一份（随工作台下载包，带 FreeCAD 的视频）

源文件：sections/*.md（Markdown + 指令，见 docs/帮助/_帮助生成/helpgen.py）、anim.js（动画与小计算器）。
文中的数一律写成 {{键}}，由计算核心当场算出（numbers()），不手写；示例都是虚构的。
"""
from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "_帮助生成"))
sys.path.insert(0, str(ROOT / "services" / "bearing"))
import helpgen as HG  # noqa: E402
from bearingkit import assembly as AS  # noqa: E402
from bearingkit import process as PR  # noqa: E402
from bearingkit import taper_thermal as TT  # noqa: E402
from bearingkit import thin as TH  # noqa: E402
from bearingkit import tolerance as TL  # noqa: E402
from bearingkit.analyze import analyse, geometry_of  # noqa: E402

EX = ROOT / "services/bearing/examples"
WEB_OUT = ROOT / "apps/bearing/public/help"
FC_ONLINE = ROOT / "apps/bearing/public/help/freecad"
MEDIA = ROOT / "apps/bearing/public/help/media"
FC_OFFLINE = ROOT / "services/bearing/freecad/help"
ONLINE = "https://wenquestrobotics.com/bearing/"  # the software, its API and the online help (the US site)
BRAND = "问渠轴承"

EDITIONS = {
    "web": dict(title="问渠轴承 · 网页版帮助", short="网页版帮助", other=("FreeCAD 版帮助", "freecad/index.html"),
                files=["web/00-intro", "web/01-start", "common/cases", "common/case-dg", "common/case-taper", "common/case-thin",
                       "common/types", "web/02-modes", "common/mfg", "common/cloud", "common/ai", "web/03-export",
                       "common/kernel", "common/arch", "common/limits", "common/faq"]),
    "freecad": dict(title="问渠轴承 · FreeCAD 工作台帮助", short="FreeCAD 版帮助", other=("网页版帮助", ONLINE + "help/index.html"),
                    files=["freecad/00-intro", "freecad/01-install", "freecad/02-use", "common/cases", "common/case-dg",
                           "common/case-taper", "common/case-thin", "freecad/03-console", "common/types", "common/mfg",
                           "common/kernel", "common/arch", "common/limits", "common/faq"]),
}

# the software's modes (?mode=) and the help section each opens (the app's help button uses the same table)
MODE_SECTION = {"design": "start", "assembly": "mfg", "quality": "mfg", "process": "mfg"}


def ex(name):
    return json.loads((EX / f"{name}.json").read_text(encoding="utf-8"))


def ck(r, cid):
    return next(c for c in r["checks"] if c["id"] == cid)


def f(x, nd=1):
    return f"{x:.{nd}f}"


# ---------- 文中的数（全部由计算核心算） ----------
def numbers():
    v = {}
    # 每类示例的校核项数
    names = sorted(p.stem for p in EX.glob("*.json"))
    v["n_examples"] = len(names)
    v["types"] = 8  # 深沟球、角接触、圆柱、圆锥（单列与成对）、谐波柔性、交叉滚子、薄壁（三种截面）
    # ---- 案例一：深沟球从头到工艺
    p = ex("demo-deep-groove")
    r = analyse(p)
    g = geometry_of(p)
    c = {x["id"]: x for x in r["checks"]}
    ch = r["chain"]
    v["dg"] = {
        "n_checks": len(r["checks"]), "status": r["status"],
        "d": g["d"], "D": g["D"], "B": g["B"], "Dw": g["Dw"], "Z": g["Z"], "fi": g["fi"], "fo": g["fo"],
        "Fr": p["loads"]["Fr"], "Fa": p["loads"]["Fa"], "n": p["loads"]["n"],
        "Pd0": f(ch["initial"] * 1000), "fit": f(ch["fit_inner"] * 1000), "therm": f(ch["thermal"] * 1000), "op": f(ch["operating"] * 1000),
        "Qmax": f(c["qmax"]["value"], 0), "loaded": c["loaded"]["value"], "p_i": f(c["p_inner"]["value"], 0), "p_o": f(c["p_outer"]["value"], 0),
        "p_lim": f(c["p_inner"]["limit"], 0), "lam": f(c["lambda"]["value"], 2), "trunc": f(c["trunc_inner"]["value"]), "sh": f(c["trunc_inner"]["limit"]),
        "unknown": "、".join(x["zh"] for x in r["checks"] if x["status"] == "unknown"),
    }
    # 载荷加大：哪一项先红
    q = copy.deepcopy(p)
    q["loads"]["Fr"] = p["loads"]["Fr"] * 1.3
    r2 = analyse(q)
    v["dg"]["Fr13"] = f(q["loads"]["Fr"], 0)
    v["dg"]["red13"] = "、".join(x["zh"] for x in r2["checks"] if x["status"] == "fail") or "没有"
    v["dg"]["p13"] = f(ck(r2, "p_inner")["value"], 0)
    # 游隙尺寸链（示例偏差，与网页“用示例偏差试一试”相同）
    dev = {"di": (4, -4), "do": (4, -4), "Dw": (0.5, -0.5), "ri": (10, -10), "ro": (10, -10)}
    nom = {"di": g["di"], "do": g["do"], "Dw": g["Dw"], "ri": g["fi"] * g["Dw"], "ro": g["fo"] * g["Dw"]}
    spec = {k: {"nom": nom[k], "es": dev[k][0] / 1000, "ei": dev[k][1] / 1000} for k in dev}
    t = TL.analyse(spec, n=100_000, target={"Pd": {"min": 0.010, "max": 0.024}})
    v["tol"] = {
        "nom": f(t["nominal"]["Pd"] * 1000), "ext_lo": f(t["extremes"]["Pd"]["min"] * 1000), "ext_hi": f(t["extremes"]["Pd"]["max"] * 1000),
        "st_lo": f(t["statistical"]["Pd"]["lo"] * 1000), "st_hi": f(t["statistical"]["Pd"]["hi"] * 1000),
        "mc_lo": f(t["montecarlo"]["Pd"]["p_lo"] * 1000), "mc_hi": f(t["montecarlo"]["Pd"]["p_hi"] * 1000),
        "out": f(t["montecarlo"]["Pd"]["outside"] * 100, 2),
        "share_do": f(t["sensitivity"]["Pd"]["do"]["share"] * 100, 0), "share_Dw": f(t["sensitivity"]["Pd"]["Dw"]["share"] * 100, 0),
        "a_lo": f(t["extremes"]["alpha0"]["min"]), "a_hi": f(t["extremes"]["alpha0"]["max"]),
    }
    # 合套选配（合成数据，与网页“用合成数据试一试”相同）
    syn = AS.synthetic(100, g["di"], g["do"], g["Dw"], g["Z"])
    a = AS.run({**syn, "P_min": 0.010, "P_max": 0.024})
    v["asm"] = {"n": a["n_inner"], "pw": len(a["piecewise"]["sets"]), "gp": a["grouped"]["count"], "gp_bad": a["grouped"]["out_of_range"],
                "left": len(a["left_inner"])}
    # 工艺（示例模板，数虚构）
    tpl = json.loads((EX / "process" / "demo-deep-groove.json").read_text(encoding="utf-8"))
    pr = PR.run(g, tpl)
    fails = [x for ring in pr["rings"].values() for x in ring["checks"] if x["status"] == "fail"] if isinstance(pr.get("rings"), dict) else []
    v["proc"] = {"fails": len(fails), "fail_what": "；".join(x["zh"] for x in fails[:2])}
    # ---- 案例二：圆锥成对，冷态调、热态校核
    p = ex("scene-tapered-pair")
    r = analyse(p)
    c = {x["id"]: x for x in r["checks"]}
    chn = r["pair"]["chain"]
    v["tp"] = {"arr": p["pair"]["arrangement"], "set": f(c["endplay"]["value"]), "work": f(c["endplay_work"]["value"]),
               "pre_work": f(c["preload_work"]["value"], 0), "rad": f(chn["radial"] * 1000), "ax": f(chn["axial"] * 1000),
               "L": p["scenario"]["L"], "Ti": p["fits"]["T_i"], "To": p["fits"]["T_o"], "Ts": p["pair"]["T_shaft"], "Th": p["pair"]["T_house"],
               "status": r["status"], "pmax": f(max(c["p_inner"]["value"], c["p_outer"]["value"]), 0)}
    # 同一根轴改背对背
    q = copy.deepcopy(p)
    q["pair"]["arrangement"] = "DB"
    rq = analyse(q)
    cq = {x["id"]: x for x in rq["checks"]}
    v["tp"]["db_work"] = f(cq["endplay_work"]["value"])
    v["tp"]["apex"] = f(rq["pair"]["chain"]["apex"], 0)
    # 冷态要调多少，热态才回到 +20 µm 的游隙（面对面）
    v["tp"]["cold_for_20"] = f(20 - (c["endplay_work"]["value"] - c["endplay"]["value"]))
    # ---- 案例三：机器人腕关节四点接触薄壁轴承
    p = ex("demo-thin-x")
    r = analyse(p)
    c = {x["id"]: x for x in r["checks"]}
    v["tx"] = {"Gr": f(c["x_gr"]["value"], 0), "pre": f(c["preload"]["value"], 0), "both": c["x_both"]["value"],
               "k_tilt": f(c["k_tilt"]["value"], 0), "mid": f(c["mid_inner"]["value"]), "p": f(c["p_inner"]["value"], 0),
               "Fr": p["loads"]["Fr"], "Fa": p["loads"]["Fa"], "M": f(p["loads"]["M"] / 1000, 0), "d": p["size"]["d"], "D": p["size"]["D"],
               "B": p["size"]["B"], "Z": p["inner"]["Z"], "Dw": p["inner"]["Dw"], "alpha": p["inner"]["alpha0_deg"]}
    for gr in (-4, 10):
        q = copy.deepcopy(p)
        q["pair"]["endplay"] = gr
        cq = {x["id"]: x for x in analyse(q)["checks"]}
        v["tx"][f"both_{'m' if gr < 0 else 'p'}{abs(gr)}"] = cq["x_both"]["value"]
        v["tx"][f"kt_{'m' if gr < 0 else 'p'}{abs(gr)}"] = f(cq["k_tilt"]["value"], 0)
    b = TH.Thin(p["inner"]["Dw"], p["inner"]["Z"], p["inner"]["dm"], p["inner"]["fi"], p["inner"]["fo"], "X", p["inner"]["alpha0_deg"], Gr=0.010)
    v["tx"]["ga10"] = f(b.free_play()["axial"] * 1000, 0)
    return v


# ---------- 动画与小计算器用的数据（计算核心真算） ----------
def anim_data(v):
    p = ex("demo-thin-x")
    spec = {"Dw": p["inner"]["Dw"], "Z": p["inner"]["Z"], "dm": p["inner"]["dm"], "fi": p["inner"]["fi"], "fo": p["inner"]["fo"],
            "section": "X", "alpha_deg": p["inner"]["alpha0_deg"]}
    P = TH.load(Fr=p["loads"]["Fr"], Fa=p["loads"]["Fa"], M=p["loads"]["M"])
    curve = TH.setting_curve(spec, P, 10.0, -20.0, 16)
    # 每个钢球的载荷，三个预紧（给“预紧量”动画）
    rings = {}
    for gr in (10, -4, -12):
        b = TH.make(spec, {"play": gr / 1000})
        c = b.contacts(b.solve(P))
        rings[str(gr)] = {"plus": [round(x, 1) for x in c["Q"][:, 0]], "minus": [round(x, 1) for x in c["Q"][:, 1]]}
    # 深沟球：钢球载荷随径向力方向（示例轴承，三档游隙）
    g = geometry_of(ex("demo-deep-groove"))
    return {"thin_curve": {k: [None if x is None else round(float(x), 2) for x in curve[k]] for k in ("e_um", "p_max", "k_tilt", "preload", "loaded")},
            "thin_rings": rings, "thin_Z": p["inner"]["Z"],
            "dg": {"Dw": g["Dw"], "Z": g["Z"], "dm": g["dm"], "fi": g["fi"], "fo": g["fo"], "di": g["di"], "do": g["do"]},
            "tp": v["tp"]}


def try_url(a, ed, online=False):
    """The web help sits at …/bearing/help/: the software is one level up. The FreeCAD copies point online."""
    from urllib.parse import quote
    q = [f"{k}={quote(a[k])}" for k in ("example", "mode", "set") if a.get(k)]
    return ("../" if ed == "web" else ONLINE) + "?" + "&".join(q)


def build(ed, vals, data, out_dir, media_prefix, api):
    return HG.build(HERE, BRAND, EDITIONS[ed], ed, vals, {**data, "api": api}, out_dir, media_prefix, try_url,
                    (HERE / "anim.js").read_text(encoding="utf-8"))


def main():
    vals = numbers()
    data = anim_data(vals)
    MEDIA.mkdir(parents=True, exist_ok=True)
    # the calculators call the software's own API: the web help sits beside it (…/bearing/help/ → ../api/), the
    # online FreeCAD copy one level deeper; the offline copy has no API (its calculators say so and link online)
    build("web", vals, data, WEB_OUT, "media/", "../api/")
    build("freecad", vals, data, FC_ONLINE, "../media/", "../../api/")
    HG.offline(lambda out, pre: build("freecad", vals, data, out, pre, ""), MEDIA, FC_OFFLINE, ONLINE + "help/media/")
    print("web", (WEB_OUT / "index.html").stat().st_size // 1024, "KB · freecad", (FC_OFFLINE / "index.html").stat().st_size // 1024, "KB ·",
          len(list(MEDIA.glob("*"))), "media files")


if __name__ == "__main__":
    if "--numbers" in sys.argv:
        print(json.dumps(numbers(), ensure_ascii=False, indent=1, default=str))
    else:
        main()
