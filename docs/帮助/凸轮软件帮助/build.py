# -*- coding: utf-8 -*-
"""问渠凸轮的网页互动帮助（第 90 轮）：一份源文件，生成两份帮助。

  python3 docs/帮助/凸轮软件帮助/build.py          （要 pip install markdown；计算核心在 services/cam）

生成（放在凸轮网页版自己的静态目录里，和软件、计算接口同一个网址，国内版、美国版都一样）：
  apps/cam/public/help/index.html                    网页版帮助（…/cam/help/）
  apps/cam/public/help/freecad/index.html            FreeCAD 版帮助的在线一份
  apps/cam/public/help/media/…                       视频、封面、字幕
  services/cam/freecad/help/…                        FreeCAD 版帮助的离线一份（随工作台下载包）

文中的数一律写成 {{键}}，由计算核心当场算出（numbers()），不手写；示例都是虚构的。
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CAM = ROOT / "services" / "cam"
sys.path.insert(0, str(HERE.parent / "_帮助生成"))
sys.path.insert(0, str(CAM))
import helpgen as HG  # noqa: E402
import app as CA  # noqa: E402  (the cam service: its view functions are what the web page shows)
import system_api as SA  # noqa: E402
from camkit import analyze as AN  # noqa: E402
from camkit import laws as LW  # noqa: E402
from camkit import measure as ME  # noqa: E402
from camkit import system_opt as OPT  # noqa: E402

EX = CAM / "examples"
WEB_OUT = ROOT / "apps/cam/public/help"
FC_ONLINE = ROOT / "apps/cam/public/help/freecad"
MEDIA = ROOT / "apps/cam/public/help/media"
FC_OFFLINE = CAM / "freecad/help"
ONLINE = "https://wenquestrobotics.com/cam/"
BRAND = "问渠凸轮"

EDITIONS = {
    "web": dict(title="问渠凸轮 · 网页版帮助", short="网页版帮助", other=("FreeCAD 版帮助", "freecad/index.html"),
                files=["web/00-intro", "web/01-start", "common/cases", "common/case-takeup", "common/case-atc", "common/methods",
                       "web/02-modes", "common/mfg", "common/cloud-ai", "web/03-export", "common/kernel", "common/arch",
                       "common/limits", "common/faq"]),
    "freecad": dict(title="问渠凸轮 · FreeCAD 工作台帮助", short="FreeCAD 版帮助", other=("网页版帮助", ONLINE + "help/index.html"),
                    files=["freecad/00-intro", "freecad/01-install", "freecad/02-use", "common/cases", "common/case-takeup",
                           "common/case-atc", "freecad/03-console", "common/methods", "common/mfg", "common/kernel", "common/arch",
                           "common/limits", "common/faq"]),
}


def ex(name):
    return json.loads((EX / f"{name}.json").read_text(encoding="utf-8"))


def f(x, nd=1):
    return f"{x:.{nd}f}"


def numbers():
    v = {"n_examples": sum(1 for p in EX.glob("*.json") if not p.name.endswith(".cae.json")), "n_laws": len(LW.LAWS)}
    v["laws"] = "、".join(x.zh for x in LW.LAWS.values())
    # ---- 案例一：平缝机挑线槽凸轮，从设计到磨削与补偿
    p = ex("sewing-takeup-groove")
    r = AN.analyse(p)
    c = {x["id"]: x for x in r["checks"]}
    m = p["mechanism"]
    rb = AN.min_base_radius(p)
    v["tk"] = {"rpm": p["loads"]["rpm"], "rb": m["rb"], "rr": m["rr"], "a": m["a"], "L": m["L"], "n_checks": len(r["checks"]),
               "phi_r": f(c["phi_rise"]["value"]), "phi_b": f(c["phi_return"]["value"]), "phi_lim": f(c["phi_rise"]["limit"], 0),
               "rho": f(c["rho_min"]["value"]), "flank": c["flank_change"]["value"], "stress": f(c["stress"]["value"], 0),
               "torque": f(c["torque"]["value"], 2), "rb_min": f(rb["rb"], 2), "status": r["status"]}
    q = copy.deepcopy(p)
    q["mfg"] = {"process": "grind", "tool_r": m["rr"], "chord_tol": 0.001}
    mv = CA.manufacture_view(q)
    mc = {x["id"]: x for x in mv["checks"]}
    v["tk"].update(gouge=f(mc["gouge"]["value"]), sim=f(mc["sim"]["value"] * 1000, 2), sim_lim=f(mc["sim"]["limit"] * 1000, 1),
                   pts=mc["points"]["value"], turn=f(mc["turn_time"]["value"], 0))
    q["measure"] = {"data": ME.synthetic(p), "format": "lift", "align": True, "a_allow": 50, "kmax": 60, "low_hi": 6}
    meas = CA.measure_view(q)
    mm = {x["id"]: x for x in meas["checks"]}
    v["tk"].update(shift=f(meas["shift_deg"], 2), acc=f(mm["acc_err"]["value"], 0), acc_lim=f(mm["acc_err"]["limit"], 0),
                   rpm_max=f(mm["rpm_max"]["value"], 0))
    q["measure"]["comp"] = {"lo": 1, "hi": 6}
    comp = CA.compensate_view(q)
    v["tk"].update(rms0=f(comp["rms_before"], 2), rms1=f(comp["rms_after"], 2))
    # the feed cam counter-example: jumps at its speed
    sf = ex("sewing-feed")
    rs = {x["id"]: x for x in AN.analyse(sf)["checks"]}
    v["fd"] = {"rpm": sf["loads"]["rpm"], "jump": f(rs["jump"]["value"], 0)}
    # ---- 案例二：加工中心换刀机构（凸轮系统）
    s = ex("atc-globoidal")
    sv = SA.system_view(s)
    sc = {x["id"]: x for x in sv["checks"]}
    opt = OPT.optimise(s)
    zh = {k: x.zh for k, x in LW.LAWS.items()}
    v["atc"] = {"rpm": s["camshaft"]["rpm"], "cycle": f(sv["cycle"], 2), "peak": f(sc["motor_peak"]["value"], 1), "rms": f(sc["motor_rms"]["value"], 1),
                "power": f(sc["power"]["value"], 0), "vib_i": f(sc["vib_index"]["value"], 0), "vib_p": f(sc["vib_plunge"]["value"], 0),
                "ratio": s["drive"]["ratio"]}
    rows = ["| 运动规律（两个凸轮都换） | 停歇时换刀臂端部残余振动 µm | 电机峰值转矩 N·m | 校核 |", "|---|---|---|---|"]
    cam_zh = {"index": "换刀臂转动凸轮", "plunge": "拔插刀凸轮"}
    ck_zh = {"pressure": "压力角", "phi_rise": "推程压力角", "phi_return": "回程压力角"}

    def fail_zh(x):
        cid, _, what = x.partition(":")
        return cam_zh.get(cid, cid) + ck_zh.get(what, what)
    for x in opt["rows"]:
        rows.append(f"| {zh.get(x['law'], x['law'])} | {x['vib_um']:.0f} | {x['motor_peak']:.1f} | "
                    f"{'没有不合格' if x['ok'] else '不合格：' + '、'.join(fail_zh(y) for y in x['fails'])} |")
    v["atc"]["opt_table"] = "\n".join(rows)
    v["atc"]["best"] = zh.get(opt["best"]["law"], opt["best"]["law"])
    cae = json.loads((EX / "atc-globoidal.cae.json").read_text(encoding="utf-8"))
    st = cae["arm"]["job"]["stats"]
    v["atc"].update(vm=f(st["vm_max_mpa"], 1), sf=f(st["safety_factor"], 1), el=st["elements"], f1=f(cae["modal"]["freqs"][0]["hz"], 0),
                    cae_date=cae["computed_at"])
    return v


def anim_data():
    out = {}
    u = np.linspace(0, 1, 101)
    for k, law in LW.LAWS.items():
        s, vv, a, _j = law.eval(u)
        out[k] = {"zh": law.zh, "s": np.round(s, 4).tolist(), "v": np.round(vv, 4).tolist(), "a": np.round(a, 4).tolist(),
                  **{c: round(float(x), 3) for c, x in LW.coefficients(k).items()}, "jump": law.end_jump}
    # measurement and compensation (case one): the error orders before and after
    p = ex("sewing-takeup-groove")
    q = copy.deepcopy(p)
    q["mfg"] = {"process": "grind", "tool_r": p["mechanism"]["rr"], "chord_tol": 0.001}
    q["measure"] = {"data": ME.synthetic(p), "format": "lift", "align": True, "a_allow": 50, "kmax": 60, "low_hi": 6, "comp": {"lo": 1, "hi": 6}}
    c = CA.compensate_view(q)
    k = c["measure"]["harm"]["k"][:24]
    return {"laws": out, "comp": {"k": k, "before": c["measure"]["harm"]["A"][:24], "after": c["after_A"][:24],
                                  "deg": c["measure"]["deg"][::4], "e": c["measure"]["e"][::4], "rest": c["remaining"][::4],
                                  "unit": c["measure"]["err_unit"]}}


def try_url(a, ed):
    from urllib.parse import quote
    q = [f"{k}={quote(a[k])}" for k in ("example", "mode", "set") if a.get(k)]
    return ("../" if ed == "web" else ONLINE) + "?" + "&".join(q)


def build(ed, vals, data, out_dir, media_prefix, api):
    return HG.build(HERE, BRAND, EDITIONS[ed], ed, vals, {**data, "api": api}, out_dir, media_prefix, try_url,
                    (HERE / "anim.js").read_text(encoding="utf-8"))


def main():
    vals = numbers()
    data = anim_data()
    MEDIA.mkdir(parents=True, exist_ok=True)
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
