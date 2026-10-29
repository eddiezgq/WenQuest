# -*- coding: utf-8 -*-
"""缝纫机设计软件的网页互动帮助（第 49 轮）：一份源文件，生成两份帮助。

  python3 docs/帮助/缝纫机软件帮助/build.py

生成：
  apps/web/src/static/help/sewing/index.html            网页版帮助（learn.wenquestrobotics.com/static/help/sewing/）
  apps/web/src/static/help/sewing-freecad/index.html    FreeCAD 版帮助的在线一份
  apps/web/src/static/help/media/…                      两份共用的视频、封面、字幕（原件就放这里，tools/ 里的录屏程序生成）
  services/gateway/app/sewcore/freecad/help/…           FreeCAD 版帮助的离线一份（随工作台安装包，带 FreeCAD 的视频）

源文件：sections/*.md（Markdown + 几种指令，见 README.md）、template.html（版式）、anim.js（动画与小计算器）。
文中的数一律由计算核心算出（{{键}}），不手写；CAE 的真实结果在 data/（tools/ 里的程序重算）。
"""
import html
import json
import math
import re
import shutil
import sys
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "services" / "gateway"))
from app.sewcore import cae_setup as CS  # noqa: E402
from app.sewcore import machines as MS  # noqa: E402
from app.sewcore import partlib as PL  # noqa: E402

WEB_OUT = ROOT / "apps/web/src/static/help/sewing"
FC_ONLINE = ROOT / "apps/web/src/static/help/sewing-freecad"
MEDIA_OUT = ROOT / "apps/web/src/static/help/media"
FC_OFFLINE = ROOT / "services/gateway/app/sewcore/freecad/help"
ONLINE = "https://learn.wenquestrobotics.com"

# 两份帮助各自的章节顺序：(文件, 编号)。common/ 两份都有；web/、freecad/ 各自的
EDITIONS = {
    "web": dict(title="缝纫机设计软件 · 网页版帮助", short="网页版帮助", other=("FreeCAD 版帮助", "../sewing-freecad/index.html"),
                files=["web/00-intro", "web/01-start", "common/cases", "common/case-lockstitch", "common/case-overlock", "common/case-cover",
                       "common/case-pattern", "common/case-flatknit", "web/02-tabs", "common/ai", "common/cae", "common/lib", "web/03-export",
                       "common/kernel", "common/arch", "web/04-account", "common/faq"]),
    "freecad": dict(title="缝纫机设计软件 · FreeCAD 工作台帮助", short="FreeCAD 版帮助", other=("网页版帮助", ONLINE + "/static/help/sewing/index.html"),
                    files=["freecad/00-intro", "freecad/01-install", "freecad/02-use", "common/cases", "common/case-lockstitch",
                               "common/case-overlock", "common/case-cover", "common/case-pattern", "common/case-flatknit", "freecad/03-console", "common/ai", "common/cae",
                           "common/lib", "common/kernel", "common/arch", "common/faq"]),
}


# ---------- 文中的数（全部由计算核心算） ----------
def numbers():
    v = {}
    for k in MS.ORDER:
        m = MS.get(k)
        R = m.analyze(m.clean({}))
        v[f"checks_{k}"] = len(R["checks"])
        v[f"name_{k}"] = m.NAME[0]
    v["checks_all"] = sum(v[f"checks_{k}"] for k in MS.ORDER)
    from app.sewcore import design as D
    R = D.analyze({})
    v["n0"] = R["params"]["n"]
    v["F_bdc"] = round(R["key"]["F_bdc"])
    v["F_lim"] = R["params"]["F_lim"]
    R6 = D.analyze(D.clean({"n": 6000}))
    v["bad6"] = "、".join(c["name"]["zh"] for c in R6["checks"] if c["state"] == "bad")
    v["n_bad6"] = sum(c["state"] == "bad" for c in R6["checks"])
    v["n_warn6"] = sum(c["state"] == "warn" for c in R6["checks"])
    R6b = D.analyze(D.clean({"n": 6000, "mr": 0.1, "fn": 240}))
    v["ok6b"] = all(c["state"] == "ok" for c in R6b["checks"])
    v["cats"] = len(PL.CATS)
    v["cat_names"] = "、".join(c["zh"] for c in PL.CATS.values())
    from app import sewing_parts as SP
    from app import sewing_cae  # noqa: F401
    v["max_parts"] = SP.MAX_PARTS
    v["extract_daily"] = SP.EXTRACT_DAILY
    from app.config import Settings
    v["ai_daily"] = Settings.model_fields["sewing_ai_daily"].default
    cae = json.loads((HERE / "data/web_cae.json").read_text())
    fc = json.loads((HERE / "data/crank_fea.json").read_text())
    v["fea_vm"] = round(cae["fea"]["vm_max_mpa"], 1)
    v["fea_sf"] = round(cae["fea"]["safety_factor"], 1)
    v["fea_el"] = cae["fea"]["elements"]
    v["fc_vm"] = fc["max"]
    v["fc_el"] = fc["elements"]
    v["fea_diff"] = round(abs(cae["fea"]["vm_max_mpa"] - fc["max"]) / cae["fea"]["vm_max_mpa"] * 100, 1)
    v["fea_force"] = round(fc["force"], 1)
    v["mbd_peak"] = round(cae["mbd"]["torque_peak_mbd"], 2)
    v["mbd_formula"] = round(cae["mbd"]["torque_peak_formula"], 2)
    v["mbd_diff"] = round(cae["mbd"]["diff"] * 100, 1)
    v["motor_pick"] = cae["motor"]["pick"]
    v["motor_peak"] = round(cae["motor"]["peak_nm"], 2)
    v["motor_rms"] = round(cae["motor"]["rms_nm"], 2)
    v["cae_date"] = cae["date"]
    v.update(case_numbers())
    return v


def case_numbers():
    """四个典型案例（第 52 轮）：tools/run_cases.py 真算的结果；文中用 {{ls.crank_fea.vm}} 这样的路径取，派生的数在这里算"""
    d = json.loads((HERE / "data/cases.json").read_text())
    v = {"ls": d["lockstitch"], "ol": d["overlock"], "cv": d["cover"], "pt": d["pattern"], "case_date": d["date"]}
    L, O, P = d["lockstitch"], d["overlock"], d["pattern"]
    pct = lambda x: round((1 - x) * 100)                                       # noqa: E731
    v["ls_topo_cut"] = pct(L["crank_topo"]["mass_ratio"])
    v["ls_cam_save"] = round(L["crank_cam"]["time_s"] - L["crank_cam_topo"]["time_s"], 1)
    v["ls_mbd_diff"] = round(L["mbd"]["diff"] * 100, 1)
    v["ls_need_rms"] = round(L["up6000_motor"]["rms"] * L["up6000_motor"]["safety"], 1)
    v["ls_need_peak"] = round(L["up6000_motor"]["peak"] * L["up6000_motor"]["safety"], 1)
    v["ls_lib_rms"] = round(L["up6000_motor_lib"]["rms_use"] * 100)
    v["ls_lib_peak"] = round(L["up6000_motor_lib"]["peak_use"] * 100)
    v["ls_chain"] = round(L["base"]["chain"]["y_int"] * 100, 1)
    v["ol_cut50"] = pct(O["rocker_topo50"]["mass_ratio"])
    v["ol_cut40"] = pct(O["rocker_topo40"]["mass_ratio"])
    v["ol_life50"] = round(O["rocker_topo50"]["verify"]["life_y"], 1)
    v["ol_opt_gamma"] = round(O["opt_upper"]["candidates"][0]["value"], 1)
    lab = {k: zh for g in MS.get("overlock").GROUPS for k, zh, *_ in g[3]}
    best = O["opt_upper"]["candidates"][0]["params"]
    v["ol_opt"] = "，".join(f"{lab[k]} = {x}" for k, x in best.items())
    Ro = MS.get("overlock").analyze(MS.get("overlock").clean(best))
    v["ol_ulswing_opt"] = next(r["value"] for r in Ro["results"] if r["zh"] == "上弯针摆角") + "°"
    tools = lambda c: "、".join(c["tools"]) + f"，{len(c['tools'])} 把刀，约 {round(c['time_s'])} 秒"     # noqa: E731
    v.update(ls_cam=tools(L["crank_cam"]), ls_cam_topo=round(L["crank_cam_topo"]["time_s"]), ol_cam_topo=tools(O["rocker_cam_topo50"]),
             ol_cam=round(O["rocker_cam"]["time_s"]), pt_cam=tools(P["template_cam"]))
    v["ls_fix_margin"] = round((1 - float(L["up6000_fix"]["F"].split("/")[0]) / 800) * 100)
    xa = P["motor_ry8"][0]["current"]
    v["pt_x_margin"] = round((xa["rated"] / xa["rms"] - 1) * 100)
    res = O["base"]["results"]
    v.update(ol_D=res["平整差动比 D*"], ol_ld=res["差动臂长 l_d = D·l_m"], ol_swing=res["下弯针摆角"], ol_tipv=res["下弯针尖最高速度"],
             ol_crit=res["下弯针偏心临界半径"], ol_ulswing=res["上弯针摆角"], ol_stroke=res["针杆行程（沿针）"])
    for k in ("ol_swing", "ol_ulswing"):
        v[k] = v[k].replace(" °", "°")
    v["ol_ratio40"] = round(O["rocker_topo40"]["verify"]["vm"] / O["rocker_topo50"]["verify"]["vm"], 1)
    for name, rec in (("ls6000", L["up6000"]),):
        for c in rec.get("warn", []) + rec.get("bad", []):
            v[f"{name}_{c['key']}"] = c["value"]
    C = d["cover"]
    rows = ["| 线迹 | 针线（每根） | 弯针线 | 覆盖线 | 每厘米线迹总耗线 | 订单总用线 | 线团 |", "|---|---|---|---|---|---|---|"]
    for st in C["stitches"]:
        need = [r for r in st["rows"] if r[0].startswith("针线")]
        lp = next((r for r in st["rows"] if r[0] == "弯针线"), None)
        cov = next((r for r in st["rows"] if r[0] == "覆盖线"), None)
        tot = next(r for r in st["rows"] if r[0] == "合计")
        rows.append(f"| {st['zh']} | {len(need)} 根 × {need[0][1]} | {lp[1] if lp else '—'} | {cov[1] if cov else '—'} | **{tot[1]}** cm/cm | {tot[2]} m | **{tot[3]}** 个 |")
    v["cv_table"] = "\n".join(rows)
    v["cv_window"] = C["window"]
    for k in ("dphi_m6", "dphi_p6"):
        v["cv_" + k] = "；".join(f"{c['name']} {c['value']}（要求 {c['limit']}）" for c in C[k]["bad"])
    v["cv_opt"] = C["opt_timing"][0]["params"]["dphi"]
    lo, hi = (float(x) for x in C["window"].split("…"))
    v["cv_wwidth"] = round(hi - lo, 1)
    v["cv_W"] = round(C["order"]["W"] * 100)
    v["cv_tol"] = round((hi - lo) / 2 - 1.5, 2)
    v.update(cv_Q=f'{C["order"]["Q"]:,.0f}', cv_L=f'{C["order"]["Lcm"]:g}', cv_cone=f'{C["order"]["cone"]:,.0f}')
    for st in C["stitches"]:
        tot = next(r for r in st["rows"] if r[0] == "合计")
        v[f"cv_m_{st['key']}"], v[f"cv_c_{st['key']}"] = tot[2], tot[3]
    m = lambda k: float(v[f"cv_m_{k}"].replace(",", ""))                   # noqa: E731
    v["cv_ratio"] = round(m("605") / m("401"), 1)
    v["pt_r_opt"] = round(P["motor_ay50"][1]["r_opt"], 1)
    v["pt_gain"] = int(P["ry8"]["per_h"]) - int(P["base"]["per_h"])
    K = d["flatknit"]
    v["fk"] = K
    sh = lambda r: round((r["timing"]["knit"][1] - r["timing"]["knit"][0]) / 3.6)          # noqa: E731
    v.update(fk_knit=sh(K["base"]), fk_knit_best=sh(K["best"]), fk_knit_cuff=sh(K["cuff1"]))
    rows = ["| 方案 | 一趟 s | 趟数 | 一片 min | 比当前 | 红灯 |", "|---|---|---|---|---|---|"]
    for r in K["base"]["variants"]:
        rows.append(f"| {r[0][0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |")
    v["fk_variants"] = "\n".join(rows)
    v["fk_v_gain"] = round((1 - K["v16"]["t_piece"] / K["base"]["t_piece"]) * 100)
    v["fk_best_gain"] = round((1 - K["best"]["t_piece"] / K["base"]["t_piece"]) * 100)
    bp = K["best"]["params"]
    v["fk_best"] = f"{bp['sys']} 个系统、按实时速度补偿、机头 {bp['v']:g} m/s、加速度 {bp['a']:g} m/s²"
    v.update(fk_tpass=f'{K["base"]["t_pass"]:.2f}', fk_D=f'{K["base"]["D"]:.0f}', fk_mass=f'{K["best_motor"]["mass"]:.0f}',
             fk_bed_tm=f'{K["bed"]["t_move"]:.2f}', fk_bed_k=K["bed"]["checks"][0]["value"].split("=")[-1].strip(),
             fk_cuff3_gap=round(K["cuff3"]["t_piece"], 2), fk_vp=round(K["best"]["params"]["v"] / (25.4 / 12) * 1000))
    cm = K["best_motor"]["current"]
    v["fk_motor_margin"] = round((cm["rated"] / cm["rms"] - 1) * 100)
    v["fk_cuff_ratio"] = round(K["cuff3"]["t_piece"] / K["cuff1"]["t_piece"] * 100)
    g = K["base"]["garment"]
    v.update(fk_g_pieces=round(g["knit_pieces"]), fk_g_link=round(g["link"]), fk_g_tot=round(g["total_pieces"]), fk_g_whole=round(g["total_whole"]),
             fk_g_E=f"{g['E_eff']:g}")
    y = P["motor_ry8"][1]["current"]
    v["pt_y8_margin"] = round((y["rated"] / y["rms"] - 1) * 100)
    v["pt_tpl"] = "{:.0f} × {:.0f} × {:.0f}".format(*P["template_cam"]["template"]["plate"])
    return v


def lookup(vals, path):
    x = vals
    for k in path.split("."):
        x = x[int(k)] if isinstance(x, list) else x[k]
    return x


# ---------- 动画用的数据 ----------
def anim_data():
    from app.sewcore import design as D
    p = D.clean({})
    rod = CS.rod_series(p, p["n"], p["mr"])
    w = 2 * math.pi * p["n"] / 60
    lam = p["r"] / p["l"]
    pos, torque = [], []
    for f in range(360):
        a = math.radians(f)
        S = math.sqrt(1 - (lam * math.sin(a)) ** 2)
        pos.append(p["r"] * (1 - math.cos(a)) + p["l"] * (1 - S))        # 针杆自上止点向下的位移 mm
        acc = p["r"] / 1000 * w * w * (math.cos(a) - lam * (math.cos(2 * a) + lam ** 2 * math.sin(a) ** 4) / S ** 3)
        torque.append(p["mr"] * acc * CS._slider_vel(p, f, p["n"]) / w)
    cae = json.loads((HERE / "data/web_cae.json").read_text())
    s = cae["mbd"]["series"] or []
    mj = []
    if s:   # MuJoCo 的结果是最后几转：试 1–3 转一段，取一转重采样到 360 点，按最相关的起点对齐（只平移相位，不改数值）
        def corr(a, b):
            ma, mb = sum(a) / len(a), sum(b) / len(b)
            num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
            return num / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b) or 1)
        best = (-2, None)
        for revs in (1, 2, 3):
            seg = s[: max(2, len(s) // revs)]
            one = [seg[int(i * len(seg) / 360)] for i in range(360)]
            for k in range(0, 360, 2):
                cand = [one[(i + k) % 360] for i in range(360)]
                c = corr(cand, torque)
                if c > best[0]:
                    best = (c, cand)
        mj = best[1]
        print("MuJoCo 与公式的相关系数", round(best[0], 4))
    fc = json.loads((HERE / "data/crank_fea.json").read_text())
    return {"crank": {"r": p["r"], "l": p["l"], "n": p["n"], "mr": p["mr"], "pos": [round(x, 3) for x in pos],
                      "rod": [round(x, 1) for x in rod], "torque": [round(x, 4) for x in torque], "mujoco": [round(x, 4) for x in mj]},
            "fea": {k: fc[k] for k in ("x", "z", "s", "t", "max", "force")},
            "frame": {"fn": p["fn"], "n": p["n"]},
            "explode": json.loads((HERE / "data/explode.json").read_text())}


# ---------- Markdown + 指令 ----------
ATTR = re.compile(r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|(\S+))')


def attrs(s):
    return {m.group(1): m.group(2) if m.group(2) is not None else m.group(3) if m.group(3) is not None else m.group(4) for m in ATTR.finditer(s)}


def directive(name, a, ed, media_prefix):
    e = html.escape
    if name == "anim":
        return f'<div class="anim" data-anim="{e(a["id"])}"></div>'
    if name == "calc":
        return f'<div class="calc" data-calc="{e(a["id"])}"></div>'
    if name == "video":
        v = a["src"]
        cap = a.get("title", "")
        return (f'<figure class="vid"><video controls preload="none" playsinline poster="{media_prefix}{v}.jpg">'
                f'<source src="{media_prefix}{v}.mp4" type="video/mp4"><track kind="subtitles" srclang="zh" label="中文" default src="{media_prefix}{v}.vtt">'
                f'</video><figcaption>▶ {e(cap)}</figcaption></figure>')
    if name == "img":
        return f'<figure class="shot"><img loading="lazy" src="{media_prefix}{e(a["src"])}" alt="{e(a.get("caption", ""))}"><figcaption>{e(a.get("caption", ""))}</figcaption></figure>'
    if name == "try":
        q = [f"machine={a.get('machine', 'lockstitch')}"]
        if a.get("tab"):
            q.append(f"tab={a['tab']}")
        if a.get("p"):
            from urllib.parse import quote
            q.append("p=" + quote(a["p"]))
        url = ("/" if ed == "web" else ONLINE + "/") + "pages/sewing/sewing?" + "&".join(q)     # 网页端用 history 路由
        return f'<a class="try" href="{e(url)}" target="_blank" rel="noopener">▶ 试一试：{e(a["label"])}</a>'
    raise ValueError("unknown directive " + name)


DIR = re.compile(r"^::(\w+)\{(.*)\}\s*$", re.M)
ONLY = re.compile(r"^::only\{(\w+)\}\s*\n(.*?)^::end\s*$", re.M | re.S)


def render(md, ed, vals, media_prefix):
    md = ONLY.sub(lambda m: m.group(2) if m.group(1) == ed else "", md)
    md = re.sub(r"\{\{([\w.]+)\}\}", lambda m: str(lookup(vals, m.group(1))), md)
    blocks = {}

    def keep(m):
        k = f"@@D{len(blocks)}@@"
        blocks[k] = directive(m.group(1), attrs(m.group(2)), ed, media_prefix)
        return "\n" + k + "\n"
    md = DIR.sub(keep, md)
    h = markdown.markdown(md, extensions=["tables", "fenced_code", "attr_list", "md_in_html"])
    for k, v in blocks.items():
        h = h.replace(f"<p>{k}</p>", v).replace(k, v)
    return h


def sections(ed, vals, media_prefix):
    out, nav = [], []
    for i, f in enumerate(EDITIONS[ed]["files"]):
        md = (HERE / "sections" / (f + ".md")).read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n", md, re.S)
        meta = dict(x.split(":", 1) for x in m.group(1).splitlines()) if m else {}
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        body = md[m.end():] if m else md
        sid = meta["id"]
        h = render(body, ed, vals, media_prefix)
        subs = []

        def h3(mm):
            hid = mm.group(1) or f"{sid}-{len(subs) + 1}"
            t = re.sub("<[^>]+>", "", mm.group(2))
            subs.append((hid, t))
            return f'<h3 id="{hid}">{mm.group(2)}</h3>'
        h = re.sub(r'<h3(?: id="([^"]*)")?>(.*?)</h3>', h3, h)
        num = f"{i:02d}"
        out.append(f'<section id="{sid}"><h2><span class="n">{num}</span>{html.escape(meta["title"])}</h2>'
                   f'<p class="lead">{meta.get("lead", "")}</p>{h}</section>')
        nav.append((sid, num, meta["title"], subs))
    return "\n".join(out), nav


def nav_html(nav):
    s = []
    for sid, num, title, subs in nav:
        s.append(f'<a href="#{sid}" data-s="{sid}"><span class="n">{num}</span>{html.escape(title)}</a>')
        for k, t in subs:
            s.append(f'<a class="sub" href="#{k}" data-s="{sid}">{html.escape(t)}</a>')
    return "\n".join(s)


def build(ed, vals, data, out_dir, media_prefix):
    E = EDITIONS[ed]
    body, nav = sections(ed, vals, media_prefix)
    t = (HERE / "template.html").read_text(encoding="utf-8")
    page = (t.replace("{{TITLE}}", E["title"]).replace("{{SHORT}}", E["short"]).replace("{{NAV}}", nav_html(nav))
             .replace("{{BODY}}", body).replace("{{OTHER_NAME}}", E["other"][0]).replace("{{OTHER_URL}}", E["other"][1])
             .replace("{{EDITION}}", ed).replace("{{API}}", "" if ed == "web" else ONLINE)
             .replace("{{DATA}}", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
             .replace("{{ANIM_JS}}", (HERE / "anim.js").read_text(encoding="utf-8")))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    return page


def main():
    vals = numbers()
    data = anim_data()
    data["cats"] = PL.cats_public()
    data["ai"] = {k: vals[k] for k in ("bad6", "n_bad6", "ok6b", "mbd_diff", "checks_lockstitch")}
    data["fatigue"] = json.loads((HERE / "data/web_cae.json").read_text())["fatigue"]
    media = MEDIA_OUT                    # 视频、封面、字幕只存一份：就放在网页版的静态目录里（录屏程序在 tools/ 里）
    media.mkdir(parents=True, exist_ok=True)
    build("web", vals, data, WEB_OUT, "../media/")
    build("freecad", vals, data, FC_ONLINE, "../media/")
    # 离线版：只带 FreeCAD 的视频（fc-*）和截图，网页版的视频点了就去在线
    if FC_OFFLINE.exists():
        shutil.rmtree(FC_OFFLINE)
    (FC_OFFLINE / "media").mkdir(parents=True)
    for f in media.glob("*"):
        if f.is_file() and (f.name.startswith("fc-") or f.suffix in (".png", ".webp", ".jpg") and not f.name.startswith("web-")):
            shutil.copy2(f, FC_OFFLINE / "media" / f.name)
    page = build("freecad", vals, data, FC_OFFLINE, "media/")
    # 离线版用 file:// 打开时浏览器多半不读旁边的字幕文件：把字幕直接写进页面（data URI）
    import base64

    def inline_vtt(m):
        p = FC_OFFLINE / "media" / m.group(1)
        return f'src="data:text/vtt;base64,{base64.b64encode(p.read_bytes()).decode()}"' if p.exists() else m.group(0)
    page = re.sub(r'src="media/([^"]+\.vtt)"', inline_vtt, page)
    # 离线版里网页版的视频改成在线地址
    page = page.replace('href="../media/', f'href="{ONLINE}/static/help/media/')          # 下载件（如案例机壳 STEP）走在线地址
    page = re.sub(r'(src|poster)="media/(web-[^"]+)"', lambda m: f'{m.group(1)}="{ONLINE}/static/help/media/{m.group(2)}"', page)
    (FC_OFFLINE / "index.html").write_text(page, encoding="utf-8")
    print("web", (WEB_OUT / "index.html").stat().st_size // 1024, "KB · freecad", (FC_OFFLINE / "index.html").stat().st_size // 1024, "KB ·",
          len(list(MEDIA_OUT.glob("*"))), "media files")


if __name__ == "__main__":
    main()
